'use client'
import React, { useEffect, useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Share2, RotateCw, Sigma } from 'lucide-react';
import ForceGraph2D, { GraphData, NodeObject, LinkObject } from 'react-force-graph-2d';

interface InfluenceMapProps {
    symbol: string | null;
}

interface ApiNode {
    id: string; 
    type: string; 
    label?: string; 
    size?: number;
}

interface ApiEdge {
    from: string; 
    to: string; 
    strength?: number;
}
interface ApiData {
  nodes: ApiNode[];
  edges: ApiEdge[];
}

export function InfluenceMap({ symbol }: InfluenceMapProps) {
    const [data, setData] = useState<GraphData>({ nodes: [], links: [] });
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [key, setKey] = useState(0); // To re-mount graph

    const fetchInfluenceMap = async (currentSymbol: string) => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch(`http://localhost:8002/api/v1/market-narrator/influence-map/${currentSymbol}`);
            if (!response.ok) {
                throw new Error(`Failed to fetch influence map for ${currentSymbol}.`);
            }
            const rawData: ApiData = await response.json();
            
            const adaptedData: GraphData = {
                nodes: rawData.nodes.map((n) => ({ ...n, id: n.id, val: n.size || 1 })),
                links: rawData.edges.map((e) => ({ ...e, source: e.from, target: e.to }))
            }
            setData(adaptedData);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An unknown error occurred.');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (symbol) {
            fetchInfluenceMap(symbol);
        } else {
            setIsLoading(false);
            setData({ nodes: [], links: [] });
        }
        setKey(prev => prev + 1); 
    }, [symbol]);
    
    const graphData = useMemo(() => data, [data]);

    const handleNodeCanvasObject = (node: NodeObject, ctx: CanvasRenderingContext2D, globalScale: number) => {
        const label = (node as any).label || '';
        const fontSize = 12 / globalScale;
        ctx.font = `${fontSize}px Sans-Serif`;
        const textWidth = ctx.measureText(label).width;
        const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);

        ctx.fillStyle = 'rgba(20, 20, 30, 0.7)';
        if(node.x !== undefined && node.y !== undefined) {
            ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, bckgDimensions[0], bckgDimensions[1]);
        }
        
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = 'white';
        if(node.x !== undefined && node.y !== undefined) {
            ctx.fillText(label, node.x, node.y);
        }
    }

    return (
        <Card className="bg-black/40 border-gray-700">
            <CardHeader className="flex flex-row items-center justify-between">
                <div className="flex items-center gap-2">
                    <Share2 className="text-cyan-400" />
                    <CardTitle className="text-white">Influence Map: {symbol || 'N/A'}</CardTitle>
                </div>
                <button onClick={() => symbol && fetchInfluenceMap(symbol)} className="text-gray-400 hover:text-white">
                    <RotateCw size={16} className={isLoading ? 'animate-spin' : ''}/>
                </button>
            </CardHeader>
            <CardContent className="h-[40vh] relative">
                {isLoading && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black/50 z-10">
                        <p>Loading Map for {symbol}...</p>
                    </div>
                )}
                {error && (
                    <div className="absolute inset-0 flex items-center justify-center bg-red-900/80 z-10">
                        <p className="text-red-300">{error}</p>
                    </div>
                )}
                {!isLoading && !error && graphData.nodes.length === 0 && (
                    <div className="absolute inset-0 flex items-center justify-center">
                        <div className="text-center text-gray-500">
                            <Sigma size={48} className="mx-auto mb-4"/>
                            <p>No influence data available for {symbol}.</p>
                        </div>
                    </div>
                )}
                
                <div className="rounded-lg overflow-hidden absolute inset-0">
                    <ForceGraph2D
                        key={key}
                        graphData={graphData}
                        nodeLabel="label"
                        nodeAutoColorBy="type"
                        linkDirectionalArrowLength={3.5}
                        linkDirectionalArrowRelPos={1}
                        linkCurvature={0.25}
                        backgroundColor="rgba(0,0,0,0)"
                        nodeCanvasObject={handleNodeCanvasObject}
                    />
                </div>
            </CardContent>
        </Card>
    );
} 