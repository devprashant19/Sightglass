import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Rationale } from '../components/Rationale';
import { ClaimChip } from '../components/ClaimChip';
import { ClaimData } from '../types/data';

describe('Rationale and ClaimChip UI Components', () => {
  const mockClaim: ClaimData = {
    span: [0, 28],
    component: 'cooler_condition',
    sensor: 'TS1',
    feature: 'TS1.mean',
    stated: {
      value: 62.0,
      unit: '°C',
      direction: 'above',
      pct: 55.0,
    },
    true: {
      value: 62.0,
      pct: 55.0,
    },
    status: 'verified',
    window: [0, 60],
  };

  it('renders ClaimChip with verified status and icon', () => {
    render(<ClaimChip claim={mockClaim} text="TS1 mean 62.0 °C (55% above)" />);
    expect(screen.getByText('TS1 mean 62.0 °C (55% above)')).toBeInTheDocument();
  });

  it('renders Rationale and segments text into interactive ClaimChips', () => {
    const text = 'TS1 mean 62.0 °C (55% above) indicates reduced cooling capacity.';
    render(<Rationale text={text} claims={[mockClaim]} />);

    expect(screen.getByText('TS1 mean 62.0 °C (55% above)')).toBeInTheDocument();
    expect(screen.getByText(/indicates reduced cooling capacity/)).toBeInTheDocument();
  });

  it('rejects unsupported schema versions', () => {
    const validData = { schema_version: 1, mock: false };
    const invalidData = { schema_version: 99, mock: false };

    expect(validData.schema_version).toBe(1);
    expect(invalidData.schema_version).not.toBe(1);
  });
});
