import '@testing-library/jest-dom';
declare const expect: jest.Expect;
declare const it: jest.It;

import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import OutfitGenerationBottomSheet from './OutfitGenerationBottomSheet';
import { randomOutfitConfiguration } from '@/lib/randomOutfitConfiguration';

const options = { occasions: ['Party', 'Gym'], styles: ['Workout', 'Classic'], moods: ['Playful'] };

it('routes sheet Surprise Me through the same coordinated shuffle callback', () => {
  const generated = jest.fn();
  const onShuffle = jest.fn(() => generated(randomOutfitConfiguration(options, () => 0)));
  render(<OutfitGenerationBottomSheet open weather={{ temperature: 72, condition: 'Clear' }} onClose={jest.fn()} onGenerate={generated} onShuffle={onShuffle} {...options} />);
  fireEvent.click(screen.getByRole('button', { name: /Surprise me/i }));
  expect(onShuffle).toHaveBeenCalledTimes(1);
  expect(generated).toHaveBeenCalledTimes(1);
  expect(generated).toHaveBeenCalledWith({ occasion: 'Party', style: 'Classic', mood: 'Playful' });
});

it('preserves deliberate settings even when they are outside the random defaults', () => {
  const onGenerate = jest.fn();
  const onShuffle = jest.fn();
  render(<OutfitGenerationBottomSheet open weather={{ temperature: 72, condition: 'Clear' }} onClose={jest.fn()} onGenerate={onGenerate} onShuffle={onShuffle} {...options} />);
  fireEvent.click(screen.getByRole('button', { name: 'Party' }));
  fireEvent.click(screen.getByRole('button', { name: 'Workout' }));
  fireEvent.click(screen.getByRole('button', { name: 'Playful' }));
  fireEvent.click(screen.getByRole('button', { name: 'Create outfit' }));
  expect(onGenerate).toHaveBeenCalledWith({ occasion: 'Party', style: 'Workout', mood: 'Playful' });
  expect(onShuffle).not.toHaveBeenCalled();
});

it('shows first-look settings immediately and generates only after an explicit action', () => {
  const onGenerate = jest.fn();
  const onShuffle = jest.fn();
  const onWeatherChange = jest.fn();
  render(<OutfitGenerationBottomSheet inline open onClose={jest.fn()} onGenerate={onGenerate} onShuffle={onShuffle}
    weather={{ temperature: 72, condition: 'Clear', fallback: true }} onWeatherChange={onWeatherChange} {...options} />);
  expect(screen.getByRole('heading', { name: 'What are you dressing for?' })).toBeVisible();
  expect(screen.getByText(/Estimated weather: 72°F/)).toBeVisible();
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  expect(onGenerate).not.toHaveBeenCalled();
  expect(onShuffle).not.toHaveBeenCalled();
  expect(screen.getByRole('button', { name: 'Create my first outfit' })).toBeDisabled();
  fireEvent.click(screen.getByRole('button', { name: 'Party' }));
  expect(screen.getByRole('button', { name: 'Party' })).toHaveAttribute('aria-pressed', 'true');
  fireEvent.click(screen.getByRole('button', { name: 'Classic' }));
  fireEvent.click(screen.getByRole('button', { name: 'Playful' }));
  fireEvent.change(screen.getByLabelText('Conditions for this look'), { target: { value: 'Cold' } });
  expect(onWeatherChange).toHaveBeenCalledWith('Cold');
  fireEvent.click(screen.getByRole('button', { name: 'Create my first outfit' }));
  expect(onGenerate).toHaveBeenCalledTimes(1);
  expect(onGenerate).toHaveBeenCalledWith({ occasion: 'Party', style: 'Classic', mood: 'Playful' });
});

it('restores settings after an unsuccessful first-look request without generating on mount', () => {
  const onGenerate = jest.fn();
  render(<OutfitGenerationBottomSheet inline open onClose={jest.fn()} onGenerate={onGenerate} onShuffle={jest.fn()}
    initialOptions={{ occasion: 'Party', style: 'Classic', mood: 'Playful' }} {...options} />);
  expect(screen.getByRole('button', { name: 'Classic' })).toHaveAttribute('aria-pressed', 'true');
  expect(screen.getByRole('button', { name: 'Create my first outfit' })).toBeEnabled();
  expect(onGenerate).not.toHaveBeenCalled();
});
