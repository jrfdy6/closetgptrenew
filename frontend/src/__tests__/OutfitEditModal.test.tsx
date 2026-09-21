import { Timestamp } from 'firebase/firestore';
import '@testing-library/jest-dom';
// Keep Jest types local; Cypress also declares global test functions.
declare const beforeEach: jest.Lifecycle;
declare const describe: jest.Describe;
declare const expect: jest.Expect;
declare const it: jest.It;
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import OutfitEditModal from '@/components/OutfitEditModal';
import { Outfit } from '@/lib/services/outfitService';
import type { ClothingItem } from '@/lib/hooks/useWardrobe';

// Mock the hooks
jest.mock('@/lib/hooks/useWardrobe', () => ({
  useWardrobe: () => ({
    items: mockWardrobeLoading ? [] : mockWardrobeItems,
    loading: mockWardrobeLoading
  })
}));

jest.mock('@/lib/hooks/useOutfits', () => ({
  useOutfits: () => ({
    updateOutfit: jest.fn(),
    fetchOutfit: mockFetchOutfit
  })
}));

let mockWardrobeLoading = false;
const mockFetchOutfit = jest.fn();

// Mock data
const mockWardrobeItems: ClothingItem[] = [
  {
    id: 'item-1',
    name: 'Blue T-Shirt',
    type: 'top',
    color: 'blue',
    brand: 'Nike',
    imageUrl: 'https://example.com/tshirt.jpg',
    userId: 'user-1',
    season: ['summer'],
    favorite: false,
    wearCount: 5,
    lastWorn: new Date('2024-01-15'),
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-15'),
    size: 'M',
    material: ['cotton'],
  },
  {
    id: 'item-2',
    name: 'Black Jeans',
    type: 'bottom',
    color: 'black',
    brand: 'Levi\'s',
    imageUrl: 'https://example.com/jeans.jpg',
    userId: 'user-1',
    season: ['all'],
    favorite: true,
    wearCount: 10,
    lastWorn: new Date('2024-01-20'),
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-20'),
    size: '32',
    material: ['denim'],
  }
];

const mockOutfit: Outfit = {
  id: 'outfit-1',
  name: 'Casual Friday',
  occasion: 'work',
  style: 'casual',
  mood: 'comfortable',
  items: [
    {
      id: 'item-1',
      name: 'Blue T-Shirt',
      category: 'top',
      style: 'casual',
      color: 'blue',
      imageUrl: 'https://example.com/tshirt.jpg',
      user_id: 'user-1'
    }
  ],
  confidenceScore: 0.9,
  reasoning: 'Perfect for casual Friday',
  createdAt: new Timestamp(1705312800, 0),
  updatedAt: new Timestamp(1705312800, 0),
  user_id: 'user-1',
  isFavorite: false,
  wearCount: 2,
  lastWorn: new Timestamp(1705312800, 0)
};

describe('OutfitEditModal', () => {
  const mockOnClose = jest.fn();
  const mockOnSave = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockWardrobeLoading = false;
  });

  it('renders modal when open', () => {
    render(
      <OutfitEditModal
        outfit={mockOutfit}
        isOpen={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    expect(screen.getByRole('heading', { name: /edit outfit/i })).toBeInTheDocument();
    expect(screen.getByDisplayValue('Casual Friday')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(
      <OutfitEditModal
        outfit={mockOutfit}
        isOpen={false}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    expect(screen.queryByRole('heading', { name: /edit outfit/i })).not.toBeInTheDocument();
  });

  it('validates required fields', async () => {
    render(
      <OutfitEditModal
        outfit={mockOutfit}
        isOpen={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    // Clear required fields
    fireEvent.change(screen.getByDisplayValue('Casual Friday'), { target: { value: '' } });
    
    // Try to save
    fireEvent.click(screen.getByRole('button', { name: /save changes/i }));

    await waitFor(() => {
      expect(screen.getByText('Outfit name is required')).toBeInTheDocument();
    });
  });

  it('shows unsaved changes indicator', () => {
    render(
      <OutfitEditModal
        outfit={mockOutfit}
        isOpen={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    // Make a change
    fireEvent.change(screen.getByDisplayValue('Casual Friday'), { 
      target: { value: 'Updated Outfit Name' } 
    });

    expect(screen.getByText(/unsaved changes/i)).toBeInTheDocument();
  });

  it('disables save button when no changes made', () => {
    render(
      <OutfitEditModal
        outfit={mockOutfit}
        isOpen={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    const saveButton = screen.getByRole('button', { name: /no changes/i });
    expect(saveButton).toBeDisabled();
  });

  it('calls onClose when cancel is clicked', () => {
    render(
      <OutfitEditModal
        outfit={mockOutfit}
        isOpen={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    fireEvent.click(screen.getByText('Cancel'));
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('calls onClose when X button is clicked', () => {
    render(
      <OutfitEditModal
        outfit={mockOutfit}
        isOpen={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /close edit outfit modal/i }));
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('validates item existence in wardrobe', async () => {
    // Create outfit with item not in wardrobe
    const outfitWithInvalidItem = {
      ...mockOutfit,
      items: [
        {
          id: 'invalid-item',
          name: 'Invalid Item',
          category: 'top',
          style: 'casual',
          color: 'red',
          imageUrl: '',
          user_id: 'user-1'
        }
      ]
    };

    render(
      <OutfitEditModal
        outfit={outfitWithInvalidItem}
        isOpen={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    // Make a change so the save action is enabled, then try to save
    fireEvent.change(screen.getByDisplayValue('Casual Friday'), {
      target: { value: 'Updated Outfit Name' }
    });
    fireEvent.click(screen.getByRole('button', { name: /save changes/i }));

    await waitFor(() => {
      expect(
        screen.getByText(/the following items are no longer in your wardrobe:/i)
      ).toBeInTheDocument();
    });
  });

  it('retains edited fields and selected items after a failed save, without fetching or closing', async () => {
    const errorLog = jest.spyOn(console, 'error').mockImplementation(() => {});
    const failedSave = jest.fn().mockRejectedValueOnce(new Error('Offline')).mockResolvedValueOnce(undefined);
    render(<OutfitEditModal outfit={mockOutfit} isOpen onClose={mockOnClose} onSave={failedSave} />);
    fireEvent.change(screen.getByDisplayValue('Casual Friday'), { target: { value: 'Keep my edits' } });
    fireEvent.click(screen.getByRole('button', { name: /save changes/i }));
    expect(await screen.findByText(/Your changes are still here/)).toBeVisible();
    expect(screen.getByDisplayValue('Keep my edits')).toBeVisible();
    expect(screen.getByText('Blue T-Shirt')).toBeVisible();
    expect(mockOnClose).not.toHaveBeenCalled();
    expect(mockFetchOutfit).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: /save changes/i }));
    await waitFor(() => expect(mockOnClose).toHaveBeenCalledTimes(1));
    expect(failedSave).toHaveBeenLastCalledWith(expect.objectContaining({ name: 'Keep my edits' }));
    errorLog.mockRestore();
  });

  it('does not label selected pieces missing while the wardrobe is loading', () => {
    mockWardrobeLoading = true;
    const { rerender } = render(<OutfitEditModal outfit={mockOutfit} isOpen onClose={mockOnClose} onSave={mockOnSave} />);
    fireEvent.change(screen.getByDisplayValue('Casual Friday'), { target: { value: 'Waiting for wardrobe' } });
    expect(screen.getByRole('status')).toHaveTextContent('Loading your wardrobe');
    expect(screen.queryByText(/Not in wardrobe/)).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: /save changes/i })).toBeDisabled();
    mockWardrobeLoading = false;
    rerender(<OutfitEditModal outfit={mockOutfit} isOpen onClose={mockOnClose} onSave={mockOnSave} />);
    expect(screen.getByRole('button', { name: /save changes/i })).toBeEnabled();
    expect(screen.queryByText(/Not in wardrobe/)).not.toBeInTheDocument();
  });

});
