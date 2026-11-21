import React from 'react';
import { ClaimData } from '../types/data';
import { ClaimChip } from './ClaimChip';

interface RationaleProps {
  text: string;
  claims: ClaimData[];
  onHoverClaim?: (claim: ClaimData | null) => void;
}

export const Rationale: React.FC<RationaleProps> = ({ text, claims, onHoverClaim }) => {
  if (!text) return <p className="text-slate-400 italic text-sm">No rationale generated.</p>;

  // Sort claims by start span
  const sortedClaims = [...claims].sort((a, b) => a.span[0] - b.span[0]);

  // Construct text chunks with interactive ClaimChips
  const elements: React.ReactNode[] = [];
  let lastIndex = 0;

  sortedClaims.forEach((claim, idx) => {
    const [start, end] = claim.span;

    // Add plain text before this claim
    if (start > lastIndex) {
      elements.push(
        <span key={`text-${lastIndex}`}>{text.substring(lastIndex, start)}</span>
      );
    }

    // Add ClaimChip for this span
    const claimText = text.substring(start, end);
    elements.push(
      <ClaimChip
        key={`claim-${idx}-${start}`}
        claim={claim}
        text={claimText}
        onHover={onHoverClaim}
      />
    );

    lastIndex = end;
  });

  // Add remaining text
  if (lastIndex < text.length) {
    elements.push(
      <span key={`text-end`}>{text.substring(lastIndex)}</span>
    );
  }

  return (
    <div className="text-slate-200 text-sm leading-relaxed font-sans bg-slate-900/60 p-4 rounded-lg border border-slate-800">
      {elements}
    </div>
  );
};
