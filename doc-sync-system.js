#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { spawn } = require('child_process');

class DocumentationSyncSystem {
    constructor() {
        this.baseDir = process.cwd();
        this.configFile = path.join(this.baseDir, '.doc-sync-config.json');
        this.stateFile = path.join(this.baseDir, '.doc-sync-state.json');
        this.config = this.loadConfig();
        this.state = this.loadState();
        this.watchers = [];
    }

    loadConfig() {
        const defaultConfig = {
            // Directories to watch for changes
            watchDirs: [
                'src',
                'components',
                'modules',
                'backend',
                'frontend',
                'api',
                'services',
                'utils',
                'lib'
            ],
            // File extensions to monitor
            watchExtensions: ['.js', '.ts', '.jsx', '.tsx', '.py', '.php', '.cs', '.java', '.go', '.rs'],
            // Documentation patterns to sync
            docPatterns: {
                'README.md': {
                    sections: ['installation', 'usage', 'api', 'examples'],
                    autoGenerate: true
                },
                'API.md': {
                    sections: ['endpoints', 'models', 'authentication'],
                    autoGenerate: true
                },
                'CHANGELOG.md': {
                    sections: ['unreleased', 'versions'],
                    autoGenerate: false
                }
            },
            // Auto-generation rules
            autoGenRules: {
                api: {
                    enabled: true,
                    patterns: ['**/api/**/*.js', '**/routes/**/*.js', '**/controllers/**/*.js'],
                    output: 'docs/API_REFERENCE.md'
                },
                components: {
                    enabled: true,
                    patterns: ['**/components/**/*.jsx', '**/components/**/*.tsx'],
                    output: 'docs/COMPONENTS.md'
                },
                modules: {
                    enabled: true,
                    patterns: ['**/modules/**/*.js', '**/modules/**/*.ts'],
                    output: 'docs/MODULES.md'
                }
            },
            // Git integration
            gitIntegration: {
                enabled: true,
                autoCommit: true,
                commitMessage: 'docs: auto-sync documentation with code changes'
            },
            // Update frequency
            syncInterval: 30000, // 30 seconds
            // Ignore patterns
            ignorePatterns: [
                'node_modules/**',
                '.git/**',
                'dist/**',
                'build/**',
                '*.log',
                '.env*'
            ]
        };

        if (fs.existsSync(this.configFile)) {
            try {
                const userConfig = JSON.parse(fs.readFileSync(this.configFile, 'utf8'));
                return { ...defaultConfig, ...userConfig };
            } catch (error) {
                console.warn('⚠️  Error loading config, using defaults:', error.message);
                return defaultConfig;
            }
        }

        // Create default config file
        fs.writeFileSync(this.configFile, JSON.stringify(defaultConfig, null, 2));
        console.log('📄 Created default configuration file: .doc-sync-config.json');
        return defaultConfig;
    }

    loadState() {
        if (fs.existsSync(this.stateFile)) {
            try {
                return JSON.parse(fs.readFileSync(this.stateFile, 'utf8'));
            } catch (error) {
                console.warn('⚠️  Error loading state, starting fresh:', error.message);
            }
        }
        return {
            lastSync: null,
            fileHashes: {},
            documentVersions: {}
        };
    }

    saveState() {
        fs.writeFileSync(this.stateFile, JSON.stringify(this.state, null, 2));
    }

    async start() {
        console.log('🚀 Starting Documentation Sync System...');
        
        // Initial scan and sync
        await this.performSync();
        
        // Start file watcher
        if (this.config.syncInterval > 0) {
            this.startWatcher();
        }
        
        console.log('✅ Documentation sync system is running!');
        console.log(`📁 Watching directories: ${this.config.watchDirs.join(', ')}`);
        console.log(`⏱️  Sync interval: ${this.config.syncInterval / 1000} seconds`);
    }

    startWatcher() {
        setInterval(async () => {
            await this.performSync();
        }, this.config.syncInterval);
    }

    async performSync() {
        console.log('🔄 Performing documentation sync...');
        
        const changes = await this.detectChanges();
        
        if (changes.length === 0) {
            console.log('📝 No changes detected');
            return;
        }

        console.log(`📋 Detected ${changes.length} changes:`);
        changes.forEach(change => {
            console.log(`   ${change.type}: ${change.file}`);
        });

        // Update documentation based on changes
        const updatedDocs = await this.updateDocumentation(changes);
        
        // Auto-generate documentation if enabled
        if (this.shouldAutoGenerate(changes)) {
            await this.autoGenerateDocumentation();
        }

        // Update state
        this.state.lastSync = new Date().toISOString();
        this.saveState();

        // Git integration
        if (this.config.gitIntegration.enabled && updatedDocs.length > 0) {
            await this.commitChanges(updatedDocs);
        }

        console.log('✅ Documentation sync completed');
    }

    async detectChanges() {
        const changes = [];
        
        for (const watchDir of this.config.watchDirs) {
            const dirPath = path.join(this.baseDir, watchDir);
            if (!fs.existsSync(dirPath)) continue;
            
            await this.scanDirectory(dirPath, changes);
        }
        
        return changes;
    }

    async scanDirectory(dir, changes) {
        try {
            const entries = fs.readdirSync(dir, { withFileTypes: true });
            
            for (const entry of entries) {
                const fullPath = path.join(dir, entry.name);
                const relativePath = path.relative(this.baseDir, fullPath);
                
                // Check ignore patterns
                if (this.shouldIgnore(relativePath)) continue;
                
                if (entry.isDirectory()) {
                    await this.scanDirectory(fullPath, changes);
                } else if (entry.isFile()) {
                    const ext = path.extname(entry.name);
                    if (this.config.watchExtensions.includes(ext)) {
                        const hash = await this.getFileHash(fullPath);
                        const lastHash = this.state.fileHashes[relativePath];
                        
                        if (hash !== lastHash) {
                            changes.push({
                                type: lastHash ? 'modified' : 'added',
                                file: relativePath,
                                path: fullPath,
                                hash: hash
                            });
                            this.state.fileHashes[relativePath] = hash;
                        }
                    }
                }
            }
        } catch (error) {
            console.warn(`⚠️  Could not scan directory ${dir}:`, error.message);
        }
    }

    shouldIgnore(filePath) {
        return this.config.ignorePatterns.some(pattern => {
            const regex = new RegExp(pattern.replace(/\*\*/g, '.*').replace(/\*/g, '[^/]*'));
            return regex.test(filePath);
        });
    }

    async getFileHash(filePath) {
        try {
            const content = fs.readFileSync(filePath);
            return crypto.createHash('md5').update(content).digest('hex');
        } catch (error) {
            return null;
        }
    }

    async updateDocumentation(changes) {
        const updatedDocs = [];
        
        // Update specific documentation files based on changes
        for (const change of changes) {
            const docUpdates = this.getDocumentationUpdates(change);
            
            for (const update of docUpdates) {
                try {
                    await this.applyDocumentationUpdate(update);
                    updatedDocs.push(update.docFile);
                } catch (error) {
                    console.error(`❌ Error updating ${update.docFile}:`, error.message);
                }
            }
        }
        
        return [...new Set(updatedDocs)];
    }

    getDocumentationUpdates(change) {
        const updates = [];
        const filePath = change.file;
        
        // Module documentation updates
        if (filePath.includes('/modules/') || filePath.includes('\\modules\\')) {
            updates.push({
                type: 'module',
                docFile: 'docs/MODULES.md',
                sourceFile: change.path,
                action: 'update'
            });
        }
        
        // API documentation updates
        if (filePath.includes('/api/') || filePath.includes('/routes/') || filePath.includes('/controllers/')) {
            updates.push({
                type: 'api',
                docFile: 'docs/API_REFERENCE.md',
                sourceFile: change.path,
                action: 'update'
            });
        }
        
        // Component documentation updates
        if (filePath.includes('/components/') && (filePath.endsWith('.jsx') || filePath.endsWith('.tsx'))) {
            updates.push({
                type: 'component',
                docFile: 'docs/COMPONENTS.md',
                sourceFile: change.path,
                action: 'update'
            });
        }
        
        // README updates for main changes
        if (filePath.includes('index.') || filePath.includes('main.') || filePath.includes('app.')) {
            updates.push({
                type: 'readme',
                docFile: 'README.md',
                sourceFile: change.path,
                action: 'update'
            });
        }
        
        return updates;
    }

    async applyDocumentationUpdate(update) {
        const docPath = path.join(this.baseDir, update.docFile);
        
        // Ensure documentation directory exists
        const docDir = path.dirname(docPath);
        if (!fs.existsSync(docDir)) {
            fs.mkdirSync(docDir, { recursive: true });
        }
        
        let docContent = '';
        if (fs.existsSync(docPath)) {
            docContent = fs.readFileSync(docPath, 'utf8');
        }
        
        // Generate updated content based on source file
        const updatedContent = await this.generateDocumentationContent(update, docContent);
        
        // Write updated documentation
        fs.writeFileSync(docPath, updatedContent);
        
        console.log(`📝 Updated ${update.docFile}`);
    }

    async generateDocumentationContent(update, existingContent) {
        const sourceContent = fs.readFileSync(update.sourceFile, 'utf8');
        const timestamp = new Date().toISOString();
        
        switch (update.type) {
            case 'module':
                return this.generateModuleDoc(update.sourceFile, sourceContent, existingContent, timestamp);
            case 'api':
                return this.generateApiDoc(update.sourceFile, sourceContent, existingContent, timestamp);
            case 'component':
                return this.generateComponentDoc(update.sourceFile, sourceContent, existingContent, timestamp);
            case 'readme':
                return this.generateReadmeUpdate(update.sourceFile, sourceContent, existingContent, timestamp);
            default:
                return existingContent;
        }
    }

    generateModuleDoc(filePath, sourceContent, existingContent, timestamp) {
        const moduleName = path.basename(filePath, path.extname(filePath));
        const relativePath = path.relative(this.baseDir, filePath);
        
        // Extract functions, classes, and exports
        const functions = this.extractFunctions(sourceContent);
        const classes = this.extractClasses(sourceContent);
        const exports = this.extractExports(sourceContent);
        
        const moduleSection = `
## ${moduleName}

**File:** \`${relativePath}\`  
**Last Updated:** ${new Date(timestamp).toLocaleString()}

### Description
${this.extractDescription(sourceContent) || 'No description available'}

### Functions
${functions.map(fn => `- \`${fn.name}\`: ${fn.description || 'No description'}`).join('\n')}

### Classes
${classes.map(cls => `- \`${cls.name}\`: ${cls.description || 'No description'}`).join('\n')}

### Exports
${exports.map(exp => `- \`${exp}\``).join('\n')}

---
`;

        // Update or append to existing content
        if (existingContent.includes(`## ${moduleName}`)) {
            // Replace existing section
            const regex = new RegExp(`## ${moduleName}[\\s\\S]*?(?=##|$)`, 'g');
            return existingContent.replace(regex, moduleSection);
        } else {
            // Append new section
            return existingContent + '\n' + moduleSection;
        }
    }

    generateApiDoc(filePath, sourceContent, existingContent, timestamp) {
        const endpoints = this.extractApiEndpoints(sourceContent);
        const relativePath = path.relative(this.baseDir, filePath);
        
        const apiSection = `
## API Endpoints - ${path.basename(filePath)}

**File:** \`${relativePath}\`  
**Last Updated:** ${new Date(timestamp).toLocaleString()}

${endpoints.map(endpoint => `
### ${endpoint.method} ${endpoint.path}

${endpoint.description || 'No description available'}

**Parameters:**
${endpoint.parameters.map(param => `- \`${param.name}\` (${param.type}): ${param.description || 'No description'}`).join('\n') || 'None'}

**Response:**
\`\`\`json
${endpoint.response || 'No example response'}
\`\`\`
`).join('\n')}

---
`;

        return this.updateDocumentationSection(existingContent, `API Endpoints - ${path.basename(filePath)}`, apiSection);
    }

    generateComponentDoc(filePath, sourceContent, existingContent, timestamp) {
        const componentName = path.basename(filePath, path.extname(filePath));
        const relativePath = path.relative(this.baseDir, filePath);
        const props = this.extractReactProps(sourceContent);
        
        const componentSection = `
## ${componentName}

**File:** \`${relativePath}\`  
**Last Updated:** ${new Date(timestamp).toLocaleString()}

### Description
${this.extractDescription(sourceContent) || 'No description available'}

### Props
${props.map(prop => `- \`${prop.name}\` (${prop.type}): ${prop.description || 'No description'}`).join('\n') || 'No props'}

### Usage Example
\`\`\`jsx
<${componentName} ${props.map(p => `${p.name}={${p.example || 'value'}}`).join(' ')} />
\`\`\`

---
`;

        return this.updateDocumentationSection(existingContent, componentName, componentSection);
    }

    generateReadmeUpdate(filePath, sourceContent, existingContent, timestamp) {
        // Update last modified timestamp in README
        const lastUpdatedRegex = /Last Updated:.*$/gm;
        const lastUpdatedLine = `Last Updated: ${new Date(timestamp).toLocaleString()}`;
        
        if (lastUpdatedRegex.test(existingContent)) {
            return existingContent.replace(lastUpdatedRegex, lastUpdatedLine);
        } else {
            // Add timestamp at the top
            return `${lastUpdatedLine}\n\n${existingContent}`;
        }
    }

    updateDocumentationSection(content, sectionName, newSection) {
        const regex = new RegExp(`## ${sectionName}[\\s\\S]*?(?=##|$)`, 'g');
        if (regex.test(content)) {
            return content.replace(regex, newSection);
        } else {
            return content + '\n' + newSection;
        }
    }

    extractFunctions(content) {
        const functionRegex = /(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)\s*=>|\w+))/g;
        const functions = [];
        let match;
        
        while ((match = functionRegex.exec(content)) !== null) {
            const name = match[1] || match[2];
            if (name) {
                functions.push({
                    name,
                    description: this.extractJSDocDescription(content, match.index)
                });
            }
        }
        
        return functions;
    }

    extractClasses(content) {
        const classRegex = /class\s+(\w+)/g;
        const classes = [];
        let match;
        
        while ((match = classRegex.exec(content)) !== null) {
            classes.push({
                name: match[1],
                description: this.extractJSDocDescription(content, match.index)
            });
        }
        
        return classes;
    }

    extractExports(content) {
        const exportRegex = /export\s+(?:default\s+)?(?:class\s+|function\s+|const\s+)?(\w+)/g;
        const exports = [];
        let match;
        
        while ((match = exportRegex.exec(content)) !== null) {
            exports.push(match[1]);
        }
        
        return exports;
    }

    extractApiEndpoints(content) {
        const routeRegex = /(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*['"`]([^'"`]+)['"`]/g;
        const endpoints = [];
        let match;
        
        while ((match = routeRegex.exec(content)) !== null) {
            endpoints.push({
                method: match[1].toUpperCase(),
                path: match[2],
                description: this.extractJSDocDescription(content, match.index),
                parameters: this.extractRouteParameters(match[2]),
                response: this.extractResponseExample(content, match.index)
            });
        }
        
        return endpoints;
    }

    extractReactProps(content) {
        const propsRegex = /interface\s+\w*Props\s*{([^}]+)}/g;
        const props = [];
        let match;
        
        while ((match = propsRegex.exec(content)) !== null) {
            const propsContent = match[1];
            const propRegex = /(\w+)(\?)?:\s*([^;]+);?/g;
            let propMatch;
            
            while ((propMatch = propRegex.exec(propsContent)) !== null) {
                props.push({
                    name: propMatch[1],
                    type: propMatch[3].trim(),
                    optional: !!propMatch[2],
                    description: '',
                    example: this.generatePropExample(propMatch[3].trim())
                });
            }
        }
        
        return props;
    }

    extractRouteParameters(path) {
        const paramRegex = /:(\w+)/g;
        const params = [];
        let match;
        
        while ((match = paramRegex.exec(path)) !== null) {
            params.push({
                name: match[1],
                type: 'string',
                description: 'Route parameter'
            });
        }
        
        return params;
    }

    extractJSDocDescription(content, position) {
        const beforePosition = content.substring(0, position);
        const lines = beforePosition.split('\n');
        
        // Look for JSDoc comment above
        for (let i = lines.length - 1; i >= Math.max(0, lines.length - 10); i--) {
            const line = lines[i].trim();
            if (line.startsWith('/**') || line.startsWith('*')) {
                const descMatch = line.match(/\*\s*(.+)/);
                if (descMatch) {
                    return descMatch[1];
                }
            }
        }
        
        return null;
    }

    extractDescription(content) {
        // Look for common description patterns
        const patterns = [
            /\/\*\*\s*\n\s*\*\s*(.+)/,
            /\/\/\s*(.+)/,
            /#\s*(.+)/
        ];
        
        for (const pattern of patterns) {
            const match = content.match(pattern);
            if (match) {
                return match[1];
            }
        }
        
        return null;
    }

    extractResponseExample(content, position) {
        // Look for res.json or return statements after the endpoint
        const afterPosition = content.substring(position);
        const jsonMatch = afterPosition.match(/res\.json\s*\(\s*({[^}]+})\s*\)/);
        if (jsonMatch) {
            return jsonMatch[1];
        }
        
        return '{}';
    }

    generatePropExample(type) {
        switch (type.toLowerCase()) {
            case 'string': return '"example"';
            case 'number': return '42';
            case 'boolean': return 'true';
            case 'array': return '[]';
            case 'object': return '{}';
            default: return 'value';
        }
    }

    shouldAutoGenerate(changes) {
        return changes.some(change => 
            this.config.autoGenRules.api.enabled && (
                change.file.includes('/api/') || 
                change.file.includes('/routes/') || 
                change.file.includes('/controllers/')
            )
        );
    }

    async autoGenerateDocumentation() {
        console.log('🔧 Auto-generating documentation...');
        
        // Generate API documentation index
        if (this.config.autoGenRules.api.enabled) {
            await this.generateApiIndex();
        }
        
        // Generate module documentation index
        if (this.config.autoGenRules.modules.enabled) {
            await this.generateModuleIndex();
        }
    }

    async generateApiIndex() {
        const apiFiles = [];
        
        for (const pattern of this.config.autoGenRules.api.patterns) {
            // Simple pattern matching
            const files = this.findFilesByPattern(pattern);
            apiFiles.push(...files);
        }
        
        const indexContent = `# API Reference

Auto-generated on: ${new Date().toLocaleString()}

## Available APIs

${apiFiles.map(file => `- [${path.basename(file)}](${path.relative(this.baseDir, file)})`).join('\n')}

## Endpoints

${apiFiles.map(file => {
    const content = fs.readFileSync(file, 'utf8');
    const endpoints = this.extractApiEndpoints(content);
    return endpoints.map(ep => `- ${ep.method} ${ep.path}`).join('\n');
}).join('\n')}
`;

        const outputPath = path.join(this.baseDir, this.config.autoGenRules.api.output);
        const outputDir = path.dirname(outputPath);
        
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        
        fs.writeFileSync(outputPath, indexContent);
        console.log(`📝 Generated ${this.config.autoGenRules.api.output}`);
    }

    async generateModuleIndex() {
        const moduleFiles = [];
        
        for (const pattern of this.config.autoGenRules.modules.patterns) {
            const files = this.findFilesByPattern(pattern);
            moduleFiles.push(...files);
        }
        
        const indexContent = `# Modules Documentation

Auto-generated on: ${new Date().toLocaleString()}

## Available Modules

${moduleFiles.map(file => {
    const moduleName = path.basename(file, path.extname(file));
    return `- [${moduleName}](${path.relative(this.baseDir, file)})`;
}).join('\n')}
`;

        const outputPath = path.join(this.baseDir, this.config.autoGenRules.modules.output);
        const outputDir = path.dirname(outputPath);
        
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        
        fs.writeFileSync(outputPath, indexContent);
        console.log(`📝 Generated ${this.config.autoGenRules.modules.output}`);
    }

    findFilesByPattern(pattern) {
        const files = [];
        const basePath = pattern.replace(/\/\*\*\/\*.*$/, '');
        const extension = pattern.match(/\*(\.\w+)$/)?.[1];
        
        try {
            this.walkDirectoryForPattern(path.join(this.baseDir, basePath), extension, files);
        } catch (error) {
            console.warn(`⚠️  Pattern matching error for ${pattern}:`, error.message);
        }
        
        return files;
    }

    walkDirectoryForPattern(dir, extension, files) {
        if (!fs.existsSync(dir)) return;
        
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        
        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);
            
            if (entry.isDirectory() && entry.name !== 'node_modules') {
                this.walkDirectoryForPattern(fullPath, extension, files);
            } else if (entry.isFile() && (!extension || fullPath.endsWith(extension))) {
                files.push(fullPath);
            }
        }
    }

    async commitChanges(updatedDocs) {
        if (!this.config.gitIntegration.autoCommit) return;
        
        try {
            // Stage documentation changes
            await this.runGitCommand(['add', ...updatedDocs]);
            
            // Check if there are changes to commit
            const status = await this.runGitCommand(['status', '--porcelain']);
            if (!status.trim()) {
                console.log('📝 No documentation changes to commit');
                return;
            }
            
            // Commit changes
            await this.runGitCommand(['commit', '-m', this.config.gitIntegration.commitMessage]);
            console.log('📝 Committed documentation changes to Git');
            
        } catch (error) {
            console.warn('⚠️  Git commit failed:', error.message);
        }
    }

    runGitCommand(args) {
        return new Promise((resolve, reject) => {
            const git = spawn('git', args, { cwd: this.baseDir });
            let output = '';
            let error = '';
            
            git.stdout.on('data', (data) => {
                output += data.toString();
            });
            
            git.stderr.on('data', (data) => {
                error += data.toString();
            });
            
            git.on('close', (code) => {
                if (code === 0) {
                    resolve(output);
                } else {
                    reject(new Error(error || `Git command failed with code ${code}`));
                }
            });
        });
    }

    stop() {
        this.watchers.forEach(watcher => watcher.close());
        console.log('🛑 Documentation sync system stopped');
    }
}

// CLI interface
if (require.main === module) {
    const args = process.argv.slice(2);
    const command = args[0] || 'start';
    
    const syncSystem = new DocumentationSyncSystem();
    
    switch (command) {
        case 'start':
            syncSystem.start().catch(console.error);
            break;
        case 'sync':
            syncSystem.performSync().then(() => process.exit(0)).catch(console.error);
            break;
        case 'init':
            console.log('📄 Configuration file created: .doc-sync-config.json');
            console.log('✏️  Edit this file to customize your documentation sync settings');
            break;
        default:
            console.log(`
📚 Documentation Sync System

Usage: node doc-sync-system.js [command]

Commands:
  start     Start the documentation sync daemon (default)
  sync      Perform a one-time sync
  init      Create configuration file only

Features:
  ✅ Automatic documentation generation
  ✅ Real-time file watching
  ✅ Git integration
  ✅ API documentation extraction
  ✅ Module documentation generation
  ✅ Component documentation for React
            `);
            break;
    }
}

module.exports = DocumentationSyncSystem;
