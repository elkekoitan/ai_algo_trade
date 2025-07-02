#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

class DocumentationHealthScanner {
    constructor() {
        this.issues = [];
        this.markdownFiles = [];
        this.baseDir = process.cwd();
    }

    async scan() {
        console.log('🔍 Starting Documentation Health Scan...');
        
        // Find all markdown files, excluding node_modules
        await this.findMarkdownFiles();
        
        console.log(`📄 Found ${this.markdownFiles.length} markdown files to scan`);
        
        // Process each file
        for (const file of this.markdownFiles) {
            await this.scanFile(file);
        }
        
        // Generate CSV report
        await this.generateReport();
        
        console.log('✅ Documentation health scan completed!');
        console.log(`📊 Total issues found: ${this.issues.length}`);
        console.log('📋 Report saved as: doc-health-raw.csv');
    }

    async findMarkdownFiles() {
        this.walkDirectory(this.baseDir);
        
        // Remove duplicates
        this.markdownFiles = [...new Set(this.markdownFiles)];
    }
    
    walkDirectory(dir) {
        try {
            const entries = fs.readdirSync(dir, { withFileTypes: true });
            
            for (const entry of entries) {
                const fullPath = path.join(dir, entry.name);
                
                if (entry.isDirectory()) {
                    // Skip node_modules directories
                    if (entry.name === 'node_modules') {
                        continue;
                    }
                    this.walkDirectory(fullPath);
                } else if (entry.isFile()) {
                    // Check if it's a markdown file
                    const ext = path.extname(entry.name).toLowerCase();
                    if (ext === '.md' || ext === '.markdown') {
                        this.markdownFiles.push(fullPath);
                    }
                }
            }
        } catch (error) {
            console.warn(`Warning: Could not read directory ${dir}: ${error.message}`);
        }
    }

    async scanFile(filePath) {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            const lines = content.split('\n');
            const relativePath = path.relative(this.baseDir, filePath);
            
            console.log(`📖 Scanning: ${relativePath}`);
            
            // Check for various issues
            this.checkLinks(content, lines, relativePath);
            this.checkMarkdownStyle(content, lines, relativePath);
            this.checkHeadingHierarchy(content, lines, relativePath);
            this.checkImages(content, lines, relativePath);
            
        } catch (error) {
            this.addIssue(filePath, 0, `File read error: ${error.message}`, 'error');
        }
    }

    checkLinks(content, lines, filePath) {
        const linkRegex = /\[([^\]]*)\]\(([^)]+)\)/g;
        let match;
        
        lines.forEach((line, index) => {
            const lineNumber = index + 1;
            let lineMatch;
            
            // Reset regex for each line
            const lineLinkRegex = /\[([^\]]*)\]\(([^)]+)\)/g;
            
            while ((lineMatch = lineLinkRegex.exec(line)) !== null) {
                const linkText = lineMatch[1];
                const linkUrl = lineMatch[2];
                
                this.validateLink(linkUrl, linkText, filePath, lineNumber);
            }
        });
    }

    validateLink(url, text, filePath, lineNumber) {
        // Check for empty links
        if (!url.trim()) {
            this.addIssue(filePath, lineNumber, 'Empty link URL', 'error');
            return;
        }

        // Check for local file references
        if (!url.startsWith('http') && !url.startsWith('mailto:') && !url.startsWith('#')) {
            const linkPath = path.resolve(path.dirname(path.resolve(this.baseDir, filePath)), url.split('#')[0]);
            
            if (!fs.existsSync(linkPath)) {
                this.addIssue(filePath, lineNumber, `Dead local link: ${url}`, 'error');
            }
        }

        // Check for suspicious URLs
        if (url.includes('localhost') || url.includes('127.0.0.1')) {
            this.addIssue(filePath, lineNumber, `Local development URL in documentation: ${url}`, 'warning');
        }

        // Check for placeholder links
        if (url.includes('example.com') || url === '#' || url === 'TODO') {
            this.addIssue(filePath, lineNumber, `Placeholder link: ${url}`, 'warning');
        }

        // Check for empty link text
        if (!text.trim()) {
            this.addIssue(filePath, lineNumber, 'Empty link text', 'warning');
        }
    }

    checkMarkdownStyle(content, lines, filePath) {
        lines.forEach((line, index) => {
            const lineNumber = index + 1;
            
            // Check for trailing spaces
            if (line.endsWith(' ') && line.trim().length > 0) {
                this.addIssue(filePath, lineNumber, 'Trailing whitespace', 'warning');
            }
            
            // Check for tabs instead of spaces
            if (line.includes('\t')) {
                this.addIssue(filePath, lineNumber, 'Tab character found (use spaces)', 'warning');
            }
            
            // Check for multiple consecutive blank lines
            if (index > 0 && line.trim() === '' && lines[index - 1].trim() === '') {
                let consecutiveBlankLines = 1;
                for (let i = index - 1; i >= 0 && lines[i].trim() === ''; i--) {
                    consecutiveBlankLines++;
                }
                if (consecutiveBlankLines > 2) {
                    this.addIssue(filePath, lineNumber, 'Multiple consecutive blank lines', 'info');
                }
            }
            
            // Check for long lines (> 120 characters)
            if (line.length > 120) {
                this.addIssue(filePath, lineNumber, `Line too long (${line.length} characters)`, 'info');
            }
        });
    }

    checkHeadingHierarchy(content, lines, filePath) {
        const headings = [];
        
        lines.forEach((line, index) => {
            const lineNumber = index + 1;
            const headingMatch = line.match(/^(#{1,6})\s+(.+)/);
            
            if (headingMatch) {
                const level = headingMatch[1].length;
                const text = headingMatch[2].trim();
                
                headings.push({ level, text, lineNumber });
                
                // Check for empty headings
                if (!text) {
                    this.addIssue(filePath, lineNumber, 'Empty heading', 'error');
                }
                
                // Check for heading with only punctuation
                if (text.match(/^[^\w\s]*$/)) {
                    this.addIssue(filePath, lineNumber, 'Heading contains only punctuation', 'warning');
                }
            }
        });
        
        // Check heading hierarchy
        for (let i = 1; i < headings.length; i++) {
            const current = headings[i];
            const previous = headings[i - 1];
            
            // Check if heading level jumps more than 1
            if (current.level > previous.level + 1) {
                this.addIssue(filePath, current.lineNumber, 
                    `Heading level jumps from H${previous.level} to H${current.level}`, 'warning');
            }
        }
        
        // Check for duplicate headings
        const headingTexts = headings.map(h => h.text.toLowerCase());
        const duplicates = headingTexts.filter((text, index) => headingTexts.indexOf(text) !== index);
        
        if (duplicates.length > 0) {
            duplicates.forEach(duplicateText => {
                const duplicateHeadings = headings.filter(h => h.text.toLowerCase() === duplicateText);
                duplicateHeadings.forEach(heading => {
                    this.addIssue(filePath, heading.lineNumber, 
                        `Duplicate heading: "${heading.text}"`, 'warning');
                });
            });
        }
    }

    checkImages(content, lines, filePath) {
        const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
        
        lines.forEach((line, index) => {
            const lineNumber = index + 1;
            let match;
            
            const lineImageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
            
            while ((match = lineImageRegex.exec(line)) !== null) {
                const altText = match[1];
                const imagePath = match[2];
                
                // Check for missing alt text
                if (!altText.trim()) {
                    this.addIssue(filePath, lineNumber, 'Image missing alt text', 'error');
                }
                
                // Check for local image files
                if (!imagePath.startsWith('http') && !imagePath.startsWith('data:')) {
                    const fullImagePath = path.resolve(path.dirname(path.resolve(this.baseDir, filePath)), imagePath);
                    
                    if (!fs.existsSync(fullImagePath)) {
                        this.addIssue(filePath, lineNumber, `Missing image file: ${imagePath}`, 'error');
                    }
                }
                
                // Check for placeholder images
                if (imagePath.includes('placeholder') || imagePath.includes('example.com')) {
                    this.addIssue(filePath, lineNumber, `Placeholder image: ${imagePath}`, 'warning');
                }
            }
        });
    }

    addIssue(file, line, issue, severity) {
        this.issues.push({
            file: path.relative(this.baseDir, file),
            line,
            issue,
            severity
        });
    }

    async generateReport() {
        const csvHeader = 'file,line,issue,severity\n';
        const csvRows = this.issues.map(issue => 
            `"${issue.file}","${issue.line}","${issue.issue.replace(/"/g, '""')}","${issue.severity}"`
        ).join('\n');
        
        const csvContent = csvHeader + csvRows;
        
        fs.writeFileSync(path.join(this.baseDir, 'doc-health-raw.csv'), csvContent);
        
        // Also generate a summary
        const summary = this.generateSummary();
        fs.writeFileSync(path.join(this.baseDir, 'doc-health-summary.txt'), summary);
    }

    generateSummary() {
        const totalFiles = this.markdownFiles.length;
        const totalIssues = this.issues.length;
        const errorCount = this.issues.filter(i => i.severity === 'error').length;
        const warningCount = this.issues.filter(i => i.severity === 'warning').length;
        const infoCount = this.issues.filter(i => i.severity === 'info').length;
        
        const filesWithIssues = new Set(this.issues.map(i => i.file)).size;
        
        return `Documentation Health Report Summary
========================================

📊 Scan Statistics:
- Total files scanned: ${totalFiles}
- Files with issues: ${filesWithIssues}
- Total issues found: ${totalIssues}

🚨 Issue Breakdown:
- Errors: ${errorCount}
- Warnings: ${warningCount}  
- Info: ${infoCount}

📈 Health Score: ${Math.round(((totalFiles - filesWithIssues) / totalFiles) * 100)}%

Top Issues by Type:
${this.getTopIssues()}

Generated: ${new Date().toISOString()}
`;
    }

    getTopIssues() {
        const issueTypes = {};
        this.issues.forEach(issue => {
            const type = issue.issue.split(':')[0];
            issueTypes[type] = (issueTypes[type] || 0) + 1;
        });
        
        return Object.entries(issueTypes)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10)
            .map(([type, count]) => `- ${type}: ${count}`)
            .join('\n');
    }
}


// Run the scanner
if (require.main === module) {
    const scanner = new DocumentationHealthScanner();
    scanner.scan().catch(console.error);
}

module.exports = DocumentationHealthScanner;
