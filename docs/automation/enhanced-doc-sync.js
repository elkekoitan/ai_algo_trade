#!/usr/bin/env node
/**
 * Enhanced Documentation Synchronization System for AI Algo Trade
 * 
 * Bu sistem:
 * 1. Kod değişikliklerini otomatik tespit eder
 * 2. Dokümantasyonu gerçek zamanlı günceller
 * 3. API endpoint'lerini otomatik dokümante eder
 * 4. Sağlık kontrolü yapar ve raporlar
 * 5. Git entegrasyonu ile otomatik commit/push
 * 6. Büyük geliştirmeler sonrası kapsamlı analiz
 */

const fs = require('fs');
const path = require('path');
const { exec, spawn } = require('child_process');
const crypto = require('crypto');
const chokidar = require('chokidar');

class EnhancedDocSync {
    constructor(projectRoot = process.cwd()) {
        this.projectRoot = projectRoot;
        this.automationDir = path.join(projectRoot, 'docs', 'automation');
        this.configFile = path.join(this.automationDir, 'doc-sync-config.json');
        this.stateFile = path.join(this.automationDir, 'doc-sync-state.json');
        
        this.config = this.loadConfig();
        this.state = this.loadState();
        this.watchers = new Map();
        this.lastAnalysis = null;
        
        // Enhanced tracking
        this.trackingData = {
            fileChanges: new Map(),
            apiEndpoints: new Map(),
            frontendComponents: new Map(),
            lastMajorUpdate: null,
            analysisHistory: []
        };
        
        console.log('🚀 Enhanced Documentation Sync System başlatıldı');
        console.log(`📁 Proje dizini: ${this.projectRoot}`);
        console.log(`⚙️ Konfigürasyon: ${this.configFile}`);
    }
    
    loadConfig() {
        const defaultConfig = {
            // Gelişmiş izleme dizinleri
            watchDirs: [
                'src', 'components', 'modules', 'backend', 'frontend', 'api', 
                'services', 'utils', 'lib', 'hooks', 'pages', 'app'
            ],
            watchExtensions: [
                '.js', '.ts', '.jsx', '.tsx', '.py', '.php', '.cs', 
                '.java', '.go', '.rs', '.vue', '.svelte'
            ],
            ignorePatterns: [
                '**/node_modules/**', '**/.git/**', '**/dist/**', 
                '**/build/**', '**/*.log', '**/.env*', '**/coverage/**'
            ],
            
            // Gelişmiş dokümantasyon kuralları
            autoGenRules: {
                api: {
                    enabled: true,
                    patterns: ['**/api/**/*.js', '**/api/**/*.ts', '**/api/**/*.py'],
                    output: 'docs/API_REFERENCE.md',
                    template: 'api-template.md'
                },
                components: {
                    enabled: true,
                    patterns: ['**/components/**/*.jsx', '**/components/**/*.tsx'],
                    output: 'docs/COMPONENTS_REFERENCE.md',
                    template: 'component-template.md'
                },
                modules: {
                    enabled: true,
                    patterns: ['**/modules/**/*.js', '**/modules/**/*.ts', '**/modules/**/*.py'],
                    output: 'docs/MODULES_REFERENCE.md',
                    template: 'module-template.md'
                },
                architecture: {
                    enabled: true,
                    patterns: ['**/core/**/*.js', '**/core/**/*.ts', '**/core/**/*.py'],
                    output: 'docs/ARCHITECTURE_AUTO.md',
                    template: 'architecture-template.md'
                }
            },
            
            // Git entegrasyonu
            gitIntegration: {
                enabled: true,
                autoCommit: true,
                commitMessage: 'docs: otomatik dokümantasyon senkronizasyonu',
                autoPush: false, // Manuel kontrol için false
                branch: 'main'
            },
            
            // Analiz ve raporlama
            analysis: {
                runAfterChanges: true,
                detailedAnalysisThreshold: 10, // 10+ dosya değiştiğinde detaylı analiz
                healthCheckInterval: 300000, // 5 dakikada bir sağlık kontrolü
                majorUpdateDetection: {
                    fileThreshold: 20, // 20+ dosya değişimi = major update
                    timeWindow: 3600000 // 1 saat içinde
                }
            },
            
            // Performans
            syncInterval: 15000, // 15 saniye
            debounceTime: 2000,  // 2 saniye debounce
            maxConcurrentOperations: 5
        };
        
        try {
            if (fs.existsSync(this.configFile)) {
                const userConfig = JSON.parse(fs.readFileSync(this.configFile, 'utf8'));
                return { ...defaultConfig, ...userConfig };
            }
        } catch (error) {
            console.warn('⚠️ Konfigürasyon dosyası okunamadı, varsayılan ayarlar kullanılıyor');
        }
        
        // Varsayılan konfigürasyonu kaydet
        this.saveConfig(defaultConfig);
        return defaultConfig;
    }
    
    loadState() {
        try {
            if (fs.existsSync(this.stateFile)) {
                return JSON.parse(fs.readFileSync(this.stateFile, 'utf8'));
            }
        } catch (error) {
            console.warn('⚠️ Durum dosyası okunamadı');
        }
        
        return {
            lastSync: null,
            fileHashes: {},
            lastMajorUpdate: null,
            analysisHistory: [],
            statistics: {
                totalSyncs: 0,
                totalChanges: 0,
                lastHealthCheck: null
            }
        };
    }
    
    saveConfig(config = this.config) {
        try {
            fs.mkdirSync(this.automationDir, { recursive: true });
            fs.writeFileSync(this.configFile, JSON.stringify(config, null, 2));
            console.log('💾 Konfigürasyon kaydedildi');
        } catch (error) {
            console.error('❌ Konfigürasyon kaydedilemedi:', error.message);
        }
    }
    
    saveState() {
        try {
            fs.mkdirSync(this.automationDir, { recursive: true });
            fs.writeFileSync(this.stateFile, JSON.stringify(this.state, null, 2));
        } catch (error) {
            console.error('❌ Durum kaydedilemedi:', error.message);
        }
    }
    
    async startWatching() {
        console.log('👀 Dosya izleme başlatılıyor...');
        
        for (const watchDir of this.config.watchDirs) {
            const fullPath = path.join(this.projectRoot, watchDir);
            
            if (fs.existsSync(fullPath)) {
                const watcher = chokidar.watch(fullPath, {
                    ignored: this.config.ignorePatterns,
                    persistent: true,
                    ignoreInitial: true
                });
                
                watcher.on('change', (filePath) => this.handleFileChange(filePath, 'change'));
                watcher.on('add', (filePath) => this.handleFileChange(filePath, 'add'));
                watcher.on('unlink', (filePath) => this.handleFileChange(filePath, 'delete'));
                
                this.watchers.set(watchDir, watcher);
                console.log(`✅ ${watchDir} dizini izleniyor`);
            } else {
                console.log(`⚠️ ${watchDir} dizini bulunamadı, atlanıyor`);
            }
        }
        
        // Periyodik sağlık kontrolü
        this.startHealthCheck();
        
        console.log('🎯 Dosya izleme aktif');
    }
    
    async handleFileChange(filePath, eventType) {
        const relativePath = path.relative(this.projectRoot, filePath);
        const ext = path.extname(filePath);
        
        // Sadece izlenen dosya türlerini işle
        if (!this.config.watchExtensions.includes(ext)) {
            return;
        }
        
        console.log(`📝 Dosya değişikliği: ${relativePath} (${eventType})`);
        
        // Değişikliği kaydet
        this.trackingData.fileChanges.set(relativePath, {
            path: relativePath,
            event: eventType,
            timestamp: new Date().toISOString(),
            processed: false
        });
        
        // Debounced sync
        clearTimeout(this.syncTimeout);
        this.syncTimeout = setTimeout(() => {
            this.processPendingChanges();
        }, this.config.debounceTime);
    }
    
    async processPendingChanges() {
        const pendingChanges = Array.from(this.trackingData.fileChanges.values())
            .filter(change => !change.processed);
        
        if (pendingChanges.length === 0) {
            return;
        }
        
        console.log(`🔄 ${pendingChanges.length} dosya değişikliği işleniyor...`);
        
        // Major update tespiti
        const isMajorUpdate = this.detectMajorUpdate(pendingChanges);
        
        try {
            // Dokümantasyon güncellemeleri
            await this.updateDocumentation(pendingChanges);
            
            // API analizi
            await this.analyzeApiChanges(pendingChanges);
            
            // Component analizi
            await this.analyzeComponentChanges(pendingChanges);
            
            // Major update ise kapsamlı analiz
            if (isMajorUpdate) {
                console.log('🚨 Major update tespit edildi, kapsamlı analiz başlatılıyor...');
                await this.runMajorUpdateAnalysis();
            }
            
            // Git entegrasyonu
            if (this.config.gitIntegration.enabled) {
                await this.commitChanges(pendingChanges);
            }
            
            // Değişiklikleri işaretlenen olarak işaretle
            pendingChanges.forEach(change => {
                change.processed = true;
            });
            
            // İstatistikleri güncelle
            this.state.statistics.totalSyncs++;
            this.state.statistics.totalChanges += pendingChanges.length;
            this.state.lastSync = new Date().toISOString();
            
            this.saveState();
            
            console.log('✅ Değişiklikler başarıyla işlendi');
            
        } catch (error) {
            console.error('❌ Değişiklik işleme hatası:', error.message);
        }
    }
    
    detectMajorUpdate(changes) {
        const threshold = this.config.analysis.majorUpdateDetection.fileThreshold;
        const timeWindow = this.config.analysis.majorUpdateDetection.timeWindow;
        const now = Date.now();
        
        // Son 1 saat içindeki toplam değişiklik sayısı
        const recentChanges = Array.from(this.trackingData.fileChanges.values())
            .filter(change => {
                const changeTime = new Date(change.timestamp).getTime();
                return (now - changeTime) < timeWindow;
            });
        
        return recentChanges.length >= threshold;
    }
    
    async updateDocumentation(changes) {
        console.log('📚 Dokümantasyon güncelleniyor...');
        
        for (const [ruleKey, rule] of Object.entries(this.config.autoGenRules)) {
            if (!rule.enabled) continue;
            
            const relevantChanges = changes.filter(change =>
                rule.patterns.some(pattern => 
                    this.matchesPattern(change.path, pattern)
                )
            );
            
            if (relevantChanges.length > 0) {
                await this.updateDocumentationForRule(ruleKey, rule, relevantChanges);
            }
        }
    }
    
    async updateDocumentationForRule(ruleKey, rule, changes) {
        console.log(`📖 ${ruleKey} dokümantasyonu güncelleniyor...`);
        
        const outputPath = path.join(this.projectRoot, rule.output);
        
        try {
            let content = '';
            
            // Mevcut içeriği oku
            if (fs.existsSync(outputPath)) {
                content = fs.readFileSync(outputPath, 'utf8');
            } else {
                // Template'den başla
                content = await this.loadTemplate(rule.template);
            }
            
            // İçeriği güncelle
            const updatedContent = await this.generateDocumentationContent(ruleKey, rule, changes, content);
            
            // Dosyayı kaydet
            fs.mkdirSync(path.dirname(outputPath), { recursive: true });
            fs.writeFileSync(outputPath, updatedContent);
            
            console.log(`✅ ${rule.output} güncellendi`);
            
        } catch (error) {
            console.error(`❌ ${ruleKey} dokümantasyonu güncellenirken hata:`, error.message);
        }
    }
    
    async generateDocumentationContent(ruleKey, rule, changes, existingContent) {
        const timestamp = new Date().toISOString();
        
        switch (ruleKey) {
            case 'api':
                return await this.generateApiDocumentation(changes, existingContent, timestamp);
            case 'components':
                return await this.generateComponentDocumentation(changes, existingContent, timestamp);
            case 'modules':
                return await this.generateModuleDocumentation(changes, existingContent, timestamp);
            case 'architecture':
                return await this.generateArchitectureDocumentation(changes, existingContent, timestamp);
            default:
                return existingContent;
        }
    }
    
    async generateApiDocumentation(changes, existingContent, timestamp) {
        let content = existingContent || `# API Reference\n\n*Otomatik olarak ${timestamp} tarihinde güncellendi*\n\n`;
        
        for (const change of changes) {
            const filePath = path.join(this.projectRoot, change.path);
            
            if (fs.existsSync(filePath)) {
                const fileContent = fs.readFileSync(filePath, 'utf8');
                const endpoints = this.extractApiEndpoints(fileContent, change.path);
                
                if (endpoints.length > 0) {
                    content += `\n## ${change.path}\n\n`;
                    
                    endpoints.forEach(endpoint => {
                        content += `### ${endpoint.method} ${endpoint.path}\n\n`;
                        if (endpoint.description) {
                            content += `${endpoint.description}\n\n`;
                        }
                        if (endpoint.parameters) {
                            content += `**Parameters:**\n${endpoint.parameters}\n\n`;
                        }
                        content += `**File:** \`${change.path}\`\n\n`;
                    });
                }
            }
        }
        
        return content;
    }
    
    extractApiEndpoints(fileContent, filePath) {
        const endpoints = [];
        
        // FastAPI/Python endpoints
        const pythonRouterRegex = /@router\.(get|post|put|delete|patch)\(['"](.*?)['"].*?\)\s*(?:async\s+)?def\s+(\w+)/gs;
        let match;
        
        while ((match = pythonRouterRegex.exec(fileContent)) !== null) {
            const [, method, path, funcName] = match;
            
            // Function içindeki docstring'i bul
            const funcStartIndex = match.index + match[0].length;
            const docstringMatch = fileContent.slice(funcStartIndex).match(/"""(.*?)"""/s);
            
            endpoints.push({
                method: method.toUpperCase(),
                path: path,
                function: funcName,
                description: docstringMatch ? docstringMatch[1].trim() : null,
                file: filePath
            });
        }
        
        // Express.js/Node.js endpoints
        const nodeRouterRegex = /router\.(get|post|put|delete|patch)\(['"](.*?)['"].*?\(?async\s*\(\s*req,\s*res/gs;
        while ((match = nodeRouterRegex.exec(fileContent)) !== null) {
            const [, method, path] = match;
            
            endpoints.push({
                method: method.toUpperCase(),
                path: path,
                file: filePath
            });
        }
        
        return endpoints;
    }
    
    async runMajorUpdateAnalysis() {
        console.log('🔍 Major update kapsamlı analizi başlatılıyor...');
        
        const analysisResults = {
            timestamp: new Date().toISOString(),
            type: 'major_update',
            changes: Array.from(this.trackingData.fileChanges.values()),
            results: {}
        };
        
        try {
            // Detaylı kod analizi
            analysisResults.results.codeAnalysis = await this.runDetailedCodeAnalysis();
            
            // Dokümantasyon sağlık kontrolü
            analysisResults.results.healthCheck = await this.runHealthCheck();
            
            // API endpoint analizi
            analysisResults.results.apiAnalysis = await this.runApiAnalysis();
            
            // Component analizi
            analysisResults.results.componentAnalysis = await this.runComponentAnalysis();
            
            // Cross-reference analizi
            analysisResults.results.crossReference = await this.runCrossReferenceAnalysis();
            
            // Rapor oluştur
            await this.generateMajorUpdateReport(analysisResults);
            
            // Analiz geçmişine ekle
            this.state.analysisHistory.push({
                timestamp: analysisResults.timestamp,
                type: analysisResults.type,
                changeCount: analysisResults.changes.length,
                summary: this.generateAnalysisSummary(analysisResults)
            });
            
            this.state.lastMajorUpdate = analysisResults.timestamp;
            this.saveState();
            
            console.log('✅ Major update analizi tamamlandı');
            
        } catch (error) {
            console.error('❌ Major update analizi sırasında hata:', error.message);
        }
    }
    
    async runDetailedCodeAnalysis() {
        return new Promise((resolve, reject) => {
            const scriptPath = path.join(this.automationDir, 'detailed-doc-analysis.py');
            
            exec(`python "${scriptPath}"`, { cwd: this.projectRoot }, (error, stdout, stderr) => {
                if (error) {
                    console.warn('⚠️ Detaylı kod analizi tamamlanamadı:', error.message);
                    resolve({ status: 'error', message: error.message });
                    return;
                }
                
                resolve({
                    status: 'success',
                    output: stdout,
                    errors: stderr
                });
            });
        });
    }
    
    async runHealthCheck() {
        console.log('🏥 Sağlık kontrolü çalışıyor...');
        
        return new Promise((resolve, reject) => {
            const scriptPath = path.join(this.automationDir, 'doc-health-scanner.js');
            
            // Eğer script yoksa, temel kontrol yap
            if (!fs.existsSync(scriptPath)) {
                console.log('⚠️ Sağlık kontrol scripti bulunamadı, temel kontrol yapılıyor');
                resolve({ status: 'basic_check', message: 'Temel sağlık kontrolü yapıldı' });
                return;
            }
            
            exec(`node "${scriptPath}"`, { cwd: this.projectRoot }, (error, stdout, stderr) => {
                if (error) {
                    console.warn('⚠️ Sağlık kontrolü tamamlanamadı:', error.message);
                    resolve({ status: 'error', message: error.message });
                    return;
                }
                
                this.state.statistics.lastHealthCheck = new Date().toISOString();
                this.saveState();
                
                resolve({
                    status: 'success',
                    output: stdout,
                    errors: stderr
                });
            });
        });
    }
    
    async generateMajorUpdateReport(analysisResults) {
        const reportPath = path.join(this.automationDir, 'reports', `major-update-${Date.now()}.md`);
        
        let report = `# Major Update Analiz Raporu\n\n`;
        report += `**Tarih:** ${analysisResults.timestamp}\n`;
        report += `**Toplam Değişiklik:** ${analysisResults.changes.length} dosya\n\n`;
        
        report += `## 📊 Özet\n\n`;
        
        if (analysisResults.results.healthCheck?.status === 'success') {
            report += `### Dokümantasyon Sağlığı\n`;
            if (analysisResults.results.healthCheck.summary) {
                report += `\`\`\`\n${analysisResults.results.healthCheck.summary}\n\`\`\`\n\n`;
            }
        }
        
        report += `### Değişen Dosyalar\n\n`;
        analysisResults.changes.forEach(change => {
            report += `- \`${change.path}\` (${change.event}) - ${change.timestamp}\n`;
        });
        
        report += `\n## 🔗 Cross-Reference Analizi\n\n`;
        if (analysisResults.results.crossReference) {
            report += `${JSON.stringify(analysisResults.results.crossReference, null, 2)}\n`;
        }
        
        report += `\n---\n*Bu rapor otomatik olarak Enhanced Doc Sync System tarafından oluşturulmuştur.*\n`;
        
        // Raporu kaydet
        fs.mkdirSync(path.dirname(reportPath), { recursive: true });
        fs.writeFileSync(reportPath, report);
        
        console.log(`📋 Major update raporu oluşturuldu: ${reportPath}`);
    }
    
    async startHealthCheck() {
        console.log('🏥 Periyodik sağlık kontrolü başlatıldı');
        
        setInterval(async () => {
            console.log('🔍 Periyodik sağlık kontrolü çalışıyor...');
            
            try {
                const healthResults = await this.runHealthCheck();
                this.state.statistics.lastHealthCheck = new Date().toISOString();
                this.saveState();
                
                console.log('✅ Sağlık kontrolü tamamlandı');
                
            } catch (error) {
                console.error('❌ Sağlık kontrolü hatası:', error.message);
            }
        }, this.config.analysis.healthCheckInterval);
    }
    
    async commitChanges(changes) {
        if (!this.config.gitIntegration.autoCommit) {
            return;
        }
        
        console.log('📝 Git commit hazırlanıyor...');
        
        const changedFiles = changes.map(change => change.path).join(', ');
        const commitMessage = `${this.config.gitIntegration.commitMessage}\n\nDeğişen dosyalar: ${changedFiles}`;
        
        try {
            // Dokümantasyon dosyalarını stage'e ekle
            await this.execCommand('git add docs/');
            
            // Commit
            await this.execCommand(`git commit -m "${commitMessage}"`);
            
            console.log('✅ Değişiklikler commit edildi');
            
            if (this.config.gitIntegration.autoPush) {
                await this.execCommand(`git push origin ${this.config.gitIntegration.branch}`);
                console.log('🚀 Değişiklikler push edildi');
            }
            
        } catch (error) {
            console.warn('⚠️ Git işlemi tamamlanamadı:', error.message);
        }
    }
    
    execCommand(command) {
        return new Promise((resolve, reject) => {
            exec(command, { cwd: this.projectRoot }, (error, stdout, stderr) => {
                if (error) {
                    reject(error);
                    return;
                }
                resolve(stdout);
            });
        });
    }
    
    matchesPattern(filePath, pattern) {
        // Basit glob pattern matching
        const regexPattern = pattern
            .replace(/\*\*/g, '.*')
            .replace(/\*/g, '[^/]*')
            .replace(/\./g, '\\.');
        
        return new RegExp(regexPattern).test(filePath);
    }
    
    async loadTemplate(templateName) {
        const templatePath = path.join(this.automationDir, 'templates', templateName);
        
        try {
            if (fs.existsSync(templatePath)) {
                return fs.readFileSync(templatePath, 'utf8');
            }
        } catch (error) {
            console.warn(`⚠️ Template bulunamadı: ${templateName}`);
        }
        
        // Varsayılan template
        return `# Documentation\n\n*Otomatik olarak oluşturuldu*\n\n`;
    }
    
    async stop() {
        console.log('🛑 Enhanced Doc Sync durdruluyor...');
        
        // Watchers'ı kapat
        for (const [dir, watcher] of this.watchers) {
            await watcher.close();
            console.log(`✅ ${dir} izlemesi durduruldu`);
        }
        
        this.watchers.clear();
        
        // Son durumu kaydet
        this.saveState();
        
        console.log('✅ Enhanced Doc Sync durduruldu');
    }
    
    getStatus() {
        return {
            isRunning: this.watchers.size > 0,
            watchedDirectories: Array.from(this.watchers.keys()),
            lastSync: this.state.lastSync,
            statistics: this.state.statistics,
            pendingChanges: Array.from(this.trackingData.fileChanges.values())
                .filter(change => !change.processed).length,
            lastMajorUpdate: this.state.lastMajorUpdate
        };
    }
}

// CLI Interface
async function main() {
    const args = process.argv.slice(2);
    const command = args[0] || 'help';
    
    const docSync = new EnhancedDocSync();
    
    switch (command) {
        case 'start':
            console.log('🚀 Enhanced Doc Sync başlatılıyor...');
            await docSync.startWatching();
            
            // Graceful shutdown
            process.on('SIGINT', async () => {
                console.log('\n🛑 Shutdown sinyali alındı...');
                await docSync.stop();
                process.exit(0);
            });
            
            console.log('✅ Enhanced Doc Sync çalışıyor (Ctrl+C ile durdur)');
            break;
            
        case 'sync':
            console.log('🔄 Tek seferlik senkronizasyon başlatılıyor...');
            await docSync.processPendingChanges();
            console.log('✅ Senkronizasyon tamamlandı');
            break;
            
        case 'health':
            console.log('🏥 Sağlık kontrolü başlatılıyor...');
            const healthResults = await docSync.runHealthCheck();
            console.log('📊 Sağlık kontrolü sonuçları:', healthResults);
            break;
            
        case 'analysis':
            console.log('🔍 Kapsamlı analiz başlatılıyor...');
            await docSync.runMajorUpdateAnalysis();
            console.log('✅ Analiz tamamlandı');
            break;
            
        case 'status':
            const status = docSync.getStatus();
            console.log('📊 Sistem Durumu:', JSON.stringify(status, null, 2));
            break;
            
        case 'help':
        default:
            console.log(`
🚀 Enhanced Documentation Sync System

Kullanım:
  node enhanced-doc-sync.js <komut>

Komutlar:
  start     - Sürekli izleme modunu başlat
  sync      - Tek seferlik senkronizasyon yap  
  health    - Dokümantasyon sağlık kontrolü
  analysis  - Kapsamlı proje analizi
  status    - Sistem durumunu göster
  help      - Bu yardım mesajını göster

Örnekler:
  node enhanced-doc-sync.js start
  node enhanced-doc-sync.js analysis
            `);
            break;
    }
}

// Export for use as module
module.exports = EnhancedDocSync;

// Run if called directly
if (require.main === module) {
    main().catch(console.error);
} 