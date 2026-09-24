import { fireEvent, render, screen } from '@testing-library/react';
import AvatarSelector from './AvatarSelector';

it('retains the supplied avatar and continues without generating or replacing it', () => {
  const onAvatarChange = jest.fn();
  const onComplete = jest.fn();
  render(<AvatarSelector currentAvatar="/saved-avatar.png" onAvatarChange={onAvatarChange} onComplete={onComplete} />);
  expect(screen.getByRole('img', { name: 'Your current avatar' })).toHaveAttribute('src', '/saved-avatar.png');
  expect(screen.getByRole('status')).toHaveTextContent('currently unavailable');
  fireEvent.error(screen.getByRole('img'));
  expect(screen.getByText('Your saved avatar could not be displayed.')).toBeVisible();
  fireEvent.click(screen.getByRole('button', { name: 'Continue' }));
  expect(onComplete).toHaveBeenCalledTimes(1);
  expect(onAvatarChange).not.toHaveBeenCalled();
});

it('does not invent an avatar when none is stored', () => {
  render(<AvatarSelector currentAvatar={null} onAvatarChange={jest.fn()} />);
  expect(screen.queryByRole('img')).not.toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Continue' })).toBeDisabled();
});
