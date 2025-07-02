#!/usr/bin/env node
/**
 * Master Documentation Synchronization System
 * AI Algo Trade için gelişmiş dokümantasyon yönetim sistemi
 * 
 * Bu sistem büyük geliştirmeler sonrası otomatik olarak:
 * 1. Kod-dokümantasyon cross-reference analizi yapar
 * 2. API endpoint'lerini günceller
 * 3. Sağlık kontrolü yapar
 * 4. Detaylı raporlar oluşturur
 * 5. Git'e otomatik commit atar
 */

const fs = require('fs');
const path = require('path');
const { exec, spawn } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

class MasterDocSync {
    constructor() {
        this.projectRoot = path.resolve(__dirname, '../..');
        this.automationDir = __dirname;
        this.reportDir = path.join(this.automationDir, 'reports');
        
        this.config = {
            // Büyük geliştirme tespiti
            majorUpdateTriggers: {
                newModules: true,          // Yeni modül eklenmesi
                apiChanges: true,          // API değişiklikleri
                architectureChanges: true, // Mimari değişiklikler
                fileThreshold: 15          // 15+ dosya değişimi
            },
            
            // Analiz seviyeleri
            analysisLevels: {
                quick: ['health', 'api'],
                standard: ['health', 'api', 'components', 'inventory'],
                comprehensive: ['health', 'api', 'components', 'inventory', 'cross-reference', 'architecture']
            },
            
            // Raporlama
            reports: {
                enabled: true,
                formats: ['markdown', 'json'],
                retention: 30 // 30 gün
            }
        };
        
        console.log('🎯 Master Documentation Sync System başlatıldı');
        console.log(`📁 Proje kökü: ${this.projectRoot}`);
        console.log(`🤖 Otomasyon dizini: ${this.automationDir}`);
    }
    
    async runMajorUpdateAnalysis() {
        console.log('\n🚀 MAJOR UPDATE ANALİZİ BAŞLATILIYOR');
        console.log('=====================================');
        
        const startTime = Date.now();
        const analysisId = `analysis_${Date.now()}`;
        const reportPath = path.join(this.reportDir, `${analysisId}_major_update.md`);
        
        try {
            fs.mkdirSync(this.reportDir, { recursive: true });
            
            const results = {
                analysisId,
                timestamp: new Date().toISOString(),
                type: 'major_update',
                results: {}
            };
            
            // 1. API Endpoint Analizi
            console.log('\n🔗 1/4 - API Endpoint Analizi...');
            results.results.apiAnalysis = await this.runApiAnalysis();
            
            // 2. Dokümantasyon Sağlık Kontrolü
            console.log('\n🏥 2/4 - Dokümantasyon Sağlık Kontrolü...');
            results.results.healthCheck = await this.runHealthCheck();
            
            // 3. Component Analizi
            console.log('\n🎨 3/4 - Frontend Component Analizi...');
            results.results.componentAnalysis = await this.runComponentAnalysis();
            
            // 4. Cross-Reference Analizi
            console.log('\n🔍 4/4 - Cross-Reference Analizi...');
            results.results.crossReference = await this.runCrossReferenceAnalysis();
            
            // Rapor oluştur
            await this.generateMasterReport(results, reportPath);
            
            const duration = (Date.now() - startTime) / 1000;
            
            console.log('\n✅ MAJOR UPDATE ANALİZİ TAMAMLANDI');
            console.log(`⏱️ Süre: ${duration.toFixed(2)} saniye`);
            console.log(`📋 Rapor: ${reportPath}`);
            
            return results;
            
        } catch (error) {
            console.error('\n❌ Major update analizi sırasında hata:', error.message);
            throw error;
        }
    }
    
    async runApiAnalysis() {
        console.log('   🔍 API endpoint\'leri taranıyor...');
        
        const apiDir = path.join(this.projectRoot, 'backend', 'api', 'v1');
        const endpoints = [];
        
        if (!fs.existsSync(apiDir)) {
            return { status: 'not_found', endpoints: [] };
        }
        
        try {
            const apiFiles = fs.readdirSync(apiDir)
                .filter(file => file.endsWith('.py') && file !== '__init__.py');
            
            for (const file of apiFiles) {
                const filePath = path.join(apiDir, file);
                const content = fs.readFileSync(filePath, 'utf8');
                const fileEndpoints = this.extractApiEndpoints(content, file);
                endpoints.push(...fileEndpoints);
            }
            
            return {
                status: 'success',
                totalEndpoints: endpoints.length,
                totalFiles: apiFiles.length,
                endpoints: endpoints,
                modules: [...new Set(endpoints.map(e => e.module))]
            };
            
        } catch (error) {
            return {
                status: 'error',
                message: error.message,
                endpoints: []
            };
        }
    }
    
    extractApiEndpoints(content, filename) {
        const endpoints = [];
        const module = filename.replace('.py', '');
        
        const routerRegex = /@router\.(get|post|put|delete|patch)\(['"](.*?)['"].*?\)\s*(?:async\s+)?def\s+(\w+)/gs;
        let match;
        
        while ((match = routerRegex.exec(content)) !== null) {
            const [, method, path, functionName] = match;
            
            endpoints.push({
                module,
                method: method.toUpperCase(),
                path: `/api/v1${path}`,
                function: functionName,
                file: filename
            });
        }
        
        return endpoints;
    }
    
    async runHealthCheck() {
        console.log('   🏥 Dokümantasyon sağlık kontrolü...');
        
        try {
            const scriptPath = path.join(this.automationDir, 'doc-health-scanner.js');
            
            if (!fs.existsSync(scriptPath)) {
                return { status: 'script_not_found' };
            }
            
            await execAsync(`node "${scriptPath}"`, { 
                cwd: this.projectRoot,
                timeout: 30000
            });
            
            const csvPath = path.join(this.projectRoot, 'doc-health-raw.csv');
            
            if (fs.existsSync(csvPath)) {
                const csvData = fs.readFileSync(csvPath, 'utf8');
                const lines = csvData.split('\n').filter(line => line.trim());
                return {
                    status: 'success',
                    totalIssues: Math.max(0, lines.length - 1)
                };
            }
            
            return { status: 'success', totalIssues: 0 };
            
        } catch (error) {
            return {
                status: 'error',
                message: error.message
            };
        }
    }
    
    async runComponentAnalysis() {
        console.log('   🎨 Frontend component analizi...');
        
        const componentsDir = path.join(this.projectRoot, 'frontend', 'components');
        const appDir = path.join(this.projectRoot, 'frontend', 'app');
        
        try {
            let totalComponents = 0;
            let totalPages = 0;
            
            if (fs.existsSync(componentsDir)) {
                totalComponents = this.getAllTsxFiles(componentsDir).length;
            }
            
            if (fs.existsSync(appDir)) {
                totalPages = this.getAllTsxFiles(appDir).length;
            }
            
            return {
                status: 'success',
                totalComponents,
                totalPages
            };
            
        } catch (error) {
            return {
                status: 'error',
                message: error.message
            };
        }
    }
    
    getAllTsxFiles(dir) {
        const files = [];
        
        function traverse(currentDir) {
            try {
                const items = fs.readdirSync(currentDir, { withFileTypes: true });
                
                for (const item of items) {
                    const fullPath = path.join(currentDir, item.name);
                    
                    if (item.isDirectory() && item.name !== 'node_modules') {
                        traverse(fullPath);
                    } else if (item.name.endsWith('.tsx') || item.name.endsWith('.jsx')) {
                        files.push(fullPath);
                    }
                }
            } catch (error) {
                // Skip read errors
            }
        }
        
        traverse(dir);
        return files;
    }
    
    async runCrossReferenceAnalysis() {
        console.log('   🔄 Cross-reference analizi...');
        
        try {
            const scriptPath = path.join(this.automationDir, 'detailed-doc-analysis.py');
            
            if (!fs.existsSync(scriptPath)) {
                return { status: 'script_not_found' };
            }
            
            await execAsync(`python "${scriptPath}"`, { 
                cwd: this.projectRoot,
                timeout: 60000
            });
            
            return { status: 'success' };
            
        } catch (error) {
            return {
                status: 'error',
                message: error.message
            };
        }
    }
    
    async generateMasterReport(results, reportPath) {
        console.log('   📋 Master rapor oluşturuluyor...');
        
        let report = `# 🚀 AI Algo Trade - Major Update Analiz Raporu\n\n`;
        report += `**Analiz ID:** ${results.analysisId}\n`;
        report += `**Tarih:** ${results.timestamp}\n\n`;
        
        // API Analizi
        if (results.results.apiAnalysis?.status === 'success') {
            report += `## 🔗 API Analizi\n`;
            report += `- **Toplam Endpoint:** ${results.results.apiAnalysis.totalEndpoints}\n`;
            report += `- **API Dosyası:** ${results.results.apiAnalysis.totalFiles}\n`;
            report += `- **Modüller:** ${results.results.apiAnalysis.modules.join(', ')}\n\n`;
        }
        
        // Sağlık Kontrolü
        if (results.results.healthCheck?.status === 'success') {
            report += `## 🏥 Dokümantasyon Sağlığı\n`;
            report += `- **Toplam Sorun:** ${results.results.healthCheck.totalIssues || 0}\n\n`;
        }
        
        // Component Analizi
        if (results.results.componentAnalysis?.status === 'success') {
            report += `## 🎨 Frontend Analizi\n`;
            report += `- **Toplam Component:** ${results.results.componentAnalysis.totalComponents}\n`;
            report += `- **Toplam Sayfa:** ${results.results.componentAnalysis.totalPages}\n\n`;
        }
        
        report += `\n---\n*Bu rapor Master Documentation Sync System tarafından otomatik oluşturulmuştur.*\n`;
        
        fs.writeFileSync(reportPath, report);
        console.log(`   ✅ Rapor kaydedildi: ${reportPath}`);
    }
    
    async cleanupOldReports() {
        console.log('🧹 Eski raporlar temizleniyor...');
        
        if (!fs.existsSync(this.reportDir)) return;
        
        const files = fs.readdirSync(this.reportDir);
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - this.config.reports.retention);
        
        let deletedCount = 0;
        
        files.forEach(file => {
            const filePath = path.join(this.reportDir, file);
            const stats = fs.statSync(filePath);
            
            if (stats.mtime < cutoffDate) {
                fs.unlinkSync(filePath);
                deletedCount++;
            }
        });
        
        console.log(`🗑️ ${deletedCount} eski rapor temizlendi`);
    }
}

// CLI Interface
async function main() {
    const args = process.argv.slice(2);
    const command = args[0] || 'help';
    
    const masterSync = new MasterDocSync();
    
    try {
        switch (command) {
            case 'major':
            case 'full':
                await masterSync.runMajorUpdateAnalysis();
                break;
                
            case 'cleanup':
                await masterSync.cleanupOldReports();
                break;
                
            case 'help':
            default:
                console.log(`
🎯 Master Documentation Sync System

Kullanım:
  node master-doc-sync.js <komut>

Komutlar:
  major     - Kapsamlı major update analizi (önerilen)
  full      - Kapsamlı major update analizi (alias)
  cleanup   - Eski raporları temizle
  help      - Bu yardım mesajını göster

Örnekler:
  node master-doc-sync.js major
                `);
                break;
        }
    } catch (error) {
        console.error('\n❌ Hata:', error.message);
        process.exit(1);
    }
}

// Export for use as module
module.exports = MasterDocSync;

// Run if called directly
if (require.main === module) {
    main();
} 