// Keep Jest assertions local to this module when Cypress also contributes globals.
declare const expect: jest.Expect;
declare const it: jest.It;
declare const describe: jest.Describe;
declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;

import '@testing-library/jest-dom';
import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import WardrobeItemDetails from '@/components/WardrobeItemDetails';

const item = {
  id: 'shirt-1', name: 'Striped shirt', type: 'Shirt', color: 'Light Gray',
  imageUrl: '/shirt.jpg', favorite: false, wearCount: 6,
  style: ['Classic'], season: ['Fall', 'Spring'], occasion: ['Business'],
  material: ['Cotton', 'Linen'], sleeveLength: 'long', fit: 'Slim',
  purchasePrice: 48, statementLevel: 0,
  metadata: {
    visualAttributes: { material: ['Cotton', 'Linen'], fit: 'Slim', pattern: 'Striped' },
    naturalDescription: 'A striped cotton and linen shirt',
    colorHarmony: { compatibleColors: ['navy'] },
  },
};

function setup(onUpdate = jest.fn().mockResolvedValue(undefined)) {
  render(<WardrobeItemDetails item={item} isOpen onClose={jest.fn()} onUpdate={onUpdate}
    onDelete={jest.fn()} onToggleFavorite={jest.fn()} onIncrementWear={jest.fn()}
    onGenerateOutfit={jest.fn()} />);
  return onUpdate;
}

describe('Wardrobe item safe editing', () => {
  beforeEach(() => {
    jest.spyOn(console, 'log').mockImplementation(() => {});
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });
  afterEach(() => jest.restoreAllMocks());

  it('sends only the changed name without dropdown normalization or metadata', async () => {
    const original = JSON.parse(JSON.stringify(item));
    const onUpdate = setup();
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'Oxford shirt' } });
    fireEvent.click(screen.getByRole('button', { name: /^Save$/ }));
    await waitFor(() => expect(onUpdate).toHaveBeenCalledWith('shirt-1', { name: 'Oxford shirt' }));
    expect(item).toEqual(original);
    expect(await screen.findByText('Changes saved.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^Saved$/ })).toBeDisabled();
  });

  it('does not save unchanged or reverted fields', () => {
    const onUpdate = setup();
    expect(screen.getByRole('button', { name: /^Save$/ })).toBeDisabled();
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'Changed' } });
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: item.name } });
    expect(screen.getByRole('button', { name: /^Save$/ })).toBeDisabled();
    expect(onUpdate).not.toHaveBeenCalled();
  });

  it('keeps the edit available for retry and reports a failed save', async () => {
    const onUpdate = setup(jest.fn().mockRejectedValueOnce(new Error('Unavailable')).mockResolvedValue(undefined));
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'Oxford shirt' } });
    fireEvent.click(screen.getByRole('button', { name: /^Save$/ }));
    expect(await screen.findByRole('alert')).toHaveTextContent('could not be saved');
    expect(screen.queryByText('Changes saved.')).not.toBeInTheDocument();
    expect(screen.getByLabelText('Name')).toHaveValue('Oxford shirt');
    fireEvent.click(screen.getByRole('button', { name: /^Save$/ }));
    await waitFor(() => expect(onUpdate).toHaveBeenCalledTimes(2));
    expect(await screen.findByText('Changes saved.')).toBeInTheDocument();
  });

  it('sends an explicit zero price without changing materials or other fields', async () => {
    const onUpdate = setup();
    fireEvent.change(screen.getByLabelText('Purchase price'), { target: { value: '0' } });
    fireEvent.click(screen.getByRole('button', { name: /^Save$/ }));
    await waitFor(() => expect(onUpdate).toHaveBeenCalledWith('shirt-1', { purchasePrice: 0 }));
  });
});
