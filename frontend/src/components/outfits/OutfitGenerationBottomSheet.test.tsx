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
  fireEvent.click(screen.getByRole('button', { name: /Surprise Me/ }));
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
  fireEvent.click(screen.getByRole('button', { name: 'Generate Look' }));
  expect(onGenerate).toHaveBeenCalledWith({ occasion: 'Party', style: 'Workout', mood: 'Playful' });
  expect(onShuffle).not.toHaveBeenCalled();
});
