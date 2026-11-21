import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface MockBannerProps {
  isMock: boolean;
}

export const MockBanner: React.FC<MockBannerProps> = ({ isMock }) => {
  if (!isMock) return null;

  return (
    <div
      role="alert"
      className="bg-amber-500/20 border-b border-amber-500/30 text-amber-300 px-4 py-2 text-sm font-medium flex items-center justify-center gap-2"
    >
      <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
      <span>
        <strong>Mock Data Notice:</strong> You are currently viewing mock/simulated data. Real pipeline exports land as training runs complete.
      </span>
    </div>
  );
};
