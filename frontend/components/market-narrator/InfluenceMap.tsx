'use client'
import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { motion } from 'framer-motion';
import { GitCommit } from 'lucide-react';
import { LinkObject, NodeObject } from 'force-graph';

// Dynamic import to prevent SSR issues
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), {
    ssr: false,
    loading: () => <div className="w-full h-80 bg-gray-800/50 rounded-lg flex items-center justify-center text-gray-400">Loading Graph...</div>
});

interface CustomNode extends NodeObject {
    id: string;
    name: string;
    val: number;
    color: string;
}

interface CustomLink extends LinkObject {
    source: string;
    target: string;
    label: string;
    color: string;
    width: number;
}

interface InfluenceMapProps {
    protagonist: string;
    correlations: Record<string, number>;
}

const assetColors = {
    FX: '#3b82f6',
    COMMODITY: '#f59e0b',
    CRYPTO: '#8b5cf6',
    INDEX: '#10b981',
    DEFAULT: '#6b7280',
};

const getAssetColor = (asset: string) => {
    if (['EUR', 'USD', 'JPY', 'GBP'].some(c => asset.includes(c))) return assetColors.FX;
    if (['XAU', 'WTI', 'OIL'].some(c => asset.includes(c))) return assetColors.COMMODITY;
    if (['BTC', 'ETH'].some(c => asset.includes(c))) return assetColors.CRYPTO;
    if (['DXY', 'SPX'].some(c => asset.includes(c))) return assetColors.INDEX;
    return assetColors.DEFAULT;
}

export default function InfluenceMap({ protagonist, correlations }: InfluenceMapProps) {
    const [graphData, setGraphData] = useState<{ nodes: CustomNode[], links: CustomLink[] }>({ nodes: [], links: [] });
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    useEffect(() => {
        const nodes: CustomNode[] = [];
        const links: CustomLink[] = [];

        // Add protagonist node
        nodes.push({
            id: protagonist,
            name: protagonist,
            val: 20, // Main node is larger
            color: getAssetColor(protagonist),
        });

        // Add correlated nodes and links
        Object.entries(correlations).forEach(([asset, corrValue]) => {
            nodes.push({
                id: asset,
                name: asset,
                val: 10,
                color: getAssetColor(asset),
            });
            links.push({
                source: protagonist,
                target: asset,
                label: `${(corrValue * 100).toFixed(0)}%`,
                color: corrValue > 0 ? 'rgba(34, 197, 94, 0.5)' : 'rgba(239, 68, 68, 0.5)',
                width: Math.abs(corrValue) * 5,
            });
        });

        setGraphData({ nodes, links });
    }, [protagonist, correlations]);

    if (!protagonist || !mounted) return null;

    return (
        <motion.div 
            className="bg-gray-900/50 rounded-2xl p-4 border border-gray-700/50 backdrop-blur-lg"
            initial={{opacity: 0, y: 20}}
            animate={{opacity: 1, y: 0}}
        >
            <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                <GitCommit className="w-5 h-5 text-cyan-400"/>
                Influence Map: {protagonist}
            </h3>
            <div className="w-full h-80 rounded-lg overflow-hidden">
                <ForceGraph2D
                    graphData={graphData}
                    nodeLabel="name"
                    nodeVal="val"
                    nodeAutoColorBy="color"
                    linkSource="source"
                    linkTarget="target"
                    linkColor={(link: any) => link.color}
                    linkWidth="width"
                    linkDirectionalParticles={2}
                    linkDirectionalParticleWidth={2}
                    linkDirectionalParticleColor={(link: any) => link.color}
                    backgroundColor="transparent"
                    nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
                        const label = node.name;
                        const fontSize = 12 / globalScale;
                        ctx.font = `${fontSize}px Sans-Serif`;
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillStyle = node.color as string;
                        ctx.fillText(label, node.x as number, node.y as number + 15);
                        
                        ctx.beginPath();
                        ctx.arc(node.x as number, node.y as number, node.val as number, 0, 2 * Math.PI, false);
                        ctx.fillStyle = node.color as string;
                        ctx.fill();
                    }}
                />
            </div>
        </motion.div>
    );
} 