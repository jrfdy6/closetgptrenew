import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { Calendar } from './calendar';
import { Label, Link, Divider } from './typography';
import { GridSkeleton } from './enhanced-loading';

it('forwards label association and external link attributes to real elements', () => {
  render(<><Label htmlFor="wardrobe-name">Wardrobe name</Label><input id="wardrobe-name" /><Link href="https://example.com" external>Reference</Link><Divider /></>);
  expect(screen.getByLabelText('Wardrobe name')).toBeInstanceOf(HTMLInputElement);
  const link = screen.getByRole('link', { name: 'Reference' });
  expect(link).toHaveAttribute('href', 'https://example.com');
  expect(link).toHaveAttribute('target', '_blank');
  expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  expect(screen.getByRole('separator')).toBeInTheDocument();
});

it('navigates and selects dates with the installed DayPicker API', () => {
  const onSelect = jest.fn();
  render(<Calendar mode="single" defaultMonth={new Date(2026, 8, 1)} selected={new Date(2026, 8, 24)} onSelect={onSelect} disabled={new Date(2026, 8, 25)} />);
  const selected = screen.getByRole('button', { name: /September 24th, 2026/ });
  expect(selected.parentElement).toHaveAttribute('aria-selected', 'true');
  expect(selected.parentElement?.className).toContain('[&>button]:bg-primary');
  expect(screen.getByRole('button', { name: /September 25th, 2026/ })).toBeDisabled();
  fireEvent.click(screen.getByRole('button', { name: /September 26th, 2026/ }));
  expect(onSelect.mock.calls[0][0]).toEqual(new Date(2026, 8, 26));
  fireEvent.click(screen.getByRole('button', { name: 'Go to the Next Month' }));
  expect(screen.getByText('October 2026')).toBeVisible();
  fireEvent.click(screen.getByRole('button', { name: 'Go to the Previous Month' }));
  expect(screen.getByText('September 2026')).toBeVisible();
});

it('applies staggered loading animation even when a custom skeleton takes no style prop', () => {
  const Item = () => <span>Loading item</span>;
  render(<GridSkeleton count={2} ItemSkeleton={Item} />);
  const items = screen.getAllByText('Loading item');
  expect(items[0].parentElement).toHaveStyle({ animationDelay: '0ms' });
  expect(items[1].parentElement).toHaveStyle({ animationDelay: '50ms' });
});
