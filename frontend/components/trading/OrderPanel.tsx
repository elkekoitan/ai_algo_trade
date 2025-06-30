import React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface OrderPanelProps {
    onPlaceOrder: () => void;
}

const OrderPanel = ({ onPlaceOrder }: OrderPanelProps) => (
  <Card className="bg-gray-900/50 border-gray-800 text-white p-4">
    <h3 className="font-bold mb-2">New Order</h3>
    <div className="space-y-4">
        <p>Order panel functionality will be here.</p>
        <Button onClick={onPlaceOrder} className="w-full bg-cyan-600 hover:bg-cyan-700">Place Order</Button>
    </div>
  </Card>
);

export default OrderPanel; 