import React from 'react';
import { Card } from '@/components/ui/card';
import { Story } from '@/lib/types/market-narrator';

const StoryDetail = ({ story }: { story: Story | null }) => {
    if(!story) return null;

    return (
        <Card className="bg-gray-900/50 border-gray-800 text-white p-4">
            <h3 className="font-bold mb-2">{story.title}</h3>
            <p>{story.summary}</p>
        </Card>
    )
};

export default StoryDetail; 