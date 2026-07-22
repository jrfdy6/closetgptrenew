import React, { useState } from 'react';
import { fireEvent, render, screen } from '@testing-library/react';

import { SkinToneSlider } from './SkinToneSlider';

function ControlledSlider() {
  const [value, setValue] = useState(50);
  return <SkinToneSlider value={value} onValueChange={setValue} />;
}

describe('SkinToneSlider', () => {
  it('is accessible and keeps the visible value synchronized with interaction', () => {
    render(<ControlledSlider />);

    const slider = screen.getByRole('slider', { name: 'Skin tone depth' });
    expect(slider).toHaveValue('50');
    expect(slider).toHaveAttribute('aria-valuetext', '50 percent skin tone depth');

    fireEvent.input(slider, { target: { value: '82' } });

    expect(slider).toHaveValue('82');
    expect(slider).toHaveAttribute('aria-valuetext', '82 percent skin tone depth');
    expect(screen.getByText('Skin tone depth: 82%')).toBeInTheDocument();
  });
});
