declare const expect: jest.Expect;
import { render, screen } from '@testing-library/react';
import LearningConfirmation from './LearningConfirmation';

it('acknowledges saved feedback without turning heuristic levels into quality claims', () => {
  render(<LearningConfirmation learning={{ messages: ['100% perfect fit'], total_feedback_count: 25,
    personalization_level: 100, confidence_level: 'high' }} />);
  expect(screen.getByRole('status')).toHaveTextContent('Feedback saved');
  expect(screen.queryByText(/trained|perfect|Highly Personalized|Good Match|100%/i)).not.toBeInTheDocument();
});
