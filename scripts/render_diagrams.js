const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const diagramsDir = path.join(__dirname, '../docs/diagrams');
const outputDir = path.join(diagramsDir, 'rendered');

if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
}

fs.readdir(diagramsDir, (err, files) => {
    if (err) {
        console.error('Could not list the directory.', err);
        process.exit(1);
    }

    files.forEach((file, index) => {
        if (file.endsWith('.md') && file !== 'README.md') {
            const filePath = path.join(diagramsDir, file);
            const content = fs.readFileSync(filePath, 'utf8');
            
            const mermaidRegex = /```mermaid([\s\S]*?)```/g;
            let match;
            let mermaidCount = 0;

            while ((match = mermaidRegex.exec(content)) !== null) {
                mermaidCount++;
                const mermaidCode = match[1];
                const baseFileName = path.basename(file, '.md');
                const outputFileName = `${baseFileName}${mermaidCount > 1 ? `_${mermaidCount}` : ''}`;

                const tempInputFile = path.join(__dirname, `temp_mermaid_${index}.mmd`);
                fs.writeFileSync(tempInputFile, mermaidCode);

                const svgOutputFile = path.join(outputDir, `${outputFileName}.svg`);
                const pngOutputFile = path.join(outputDir, `${outputFileName}.png`);

                try {
                    console.log(`🎨 Rendering ${outputFileName}.svg...`);
                    execSync(`npx mmdc -i ${tempInputFile} -o ${svgOutputFile} -w 1920 -H 1080`);
                    
                    console.log(`🖼️ Rendering ${outputFileName}.png...`);
                    execSync(`npx mmdc -i ${tempInputFile} -o ${pngOutputFile} -w 1920 -H 1080`);
                    
                    console.log(`✅ Successfully rendered ${outputFileName}`);

                } catch (error) {
                    console.error(`❌ Failed to render ${outputFileName}`, error);
                } finally {
                    fs.unlinkSync(tempInputFile); // Clean up temp file
                }
            }
        }
    });
}); 