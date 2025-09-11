import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import OutfitEditModal from '@/components/OutfitEditModal';
import { Outfit } from '@/lib/services/outfitService';
import { ClothingItem } from '@/lib/services/outfitService';

// Mock the hooks
jest.mock('@/lib/hooks/useWardrobe', () => ({
  useWardrobe: () => ({
    items: mockWardrobeItems
  })
}));

jest.mock('@/lib/hooks/useOutfits', () => ({
  useOutfits: () => ({
    updateOutfit: jest.fn(),
    fetchOutfit: jest.fn()
  })
}));

// Mock data
const mockWardrobeItems: ClothingItem[] = [
  {
    id: 'item-1',
    name: 'Blue T-Shirt',
    type: 'top',
    color: 'blue',
    brand: 'Nike',
    imageUrl: 'https://example.com/tshirt.jpg',
    user_id: 'user-1',
    season: 'summer',
    isFavorite: false,
    wearCount: 5,
    lastWorn: '2024-01-15',
    createdAt: '2024-01-01',
    updatedAt: '2024-01-15',
    size: 'M',
    material: 'cotton',
    condition: 'good',
    price: 25,
    purchaseDate: '2024-01-01',
    tags: ['casual'],
    notes: 'Comfortable everyday shirt'
  },
  {
    id: 'item-2',
    name: 'Black Jeans',
    type: 'bottom',
    color: 'black',
    brand: 'Levi\'s',
    imageUrl: 'https://example.com/jeans.jpg',
    user_id: 'user-1',
    season: 'all',
    isFavorite: true,
    wearCount: 10,
    lastWorn: '2024-01-20',
    createdAt: '2024-01-01',
    updatedAt: '2024-01-20',
    size: '32',
    material: 'denim',
    condition: 'good',
    price: 80,
    purchaseDate: '2024-01-01',
    tags: ['casual', 'work'],
    notes: 'Perfect fit'
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
  createdAt: { seconds: 1705312800, nanoseconds: 0, toDate: () => new Date('2024-01-15'), toMillis: () => 1705312800000, isEqual: () => false },
  updatedAt: { seconds: 1705312800, nanoseconds: 0, toDate: () => new Date('2024-01-15'), toMillis: () => 1705312800000, isEqual: () => false },
  user_id: 'user-1',
  isFavorite: false,
  wearCount: 2,
  lastWorn: { seconds: 1705312800, nanoseconds: 0, toDate: () => new Date('2024-01-15'), toMillis: () => 1705312800000, isEqual: () => false }
};

describe('OutfitEditModal', () => {
  const mockOnClose = jest.fn();
  const mockOnSave = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
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

    expect(screen.getByText('Edit Outfit')).toBeInTheDocument();
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

    expect(screen.queryByText('Edit Outfit')).not.toBeInTheDocument();
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
    fireEvent.click(screen.getByText('Save Changes'));

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

    expect(screen.getByText('Unsaved Changes')).toBeInTheDocument();
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

    const saveButton = screen.getByText('No Changes');
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

    fireEvent.click(screen.getByRole('button', { name: /close/i }));
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

    // Try to save
    fireEvent.click(screen.getByText('Save Changes'));

    await waitFor(() => {
      expect(screen.getByText(/no longer in your wardrobe/)).toBeInTheDocument();
    });
  });
});
