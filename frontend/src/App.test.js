import { render, screen } from '@testing-library/react';
import App from './App';

jest.mock('@monaco-editor/react', () => {
  return function MockMonacoEditor() {
    return <div data-testid="mock-editor">Mock Editor</div>;
  };
});

test('renders AI Code Mentor title', () => {
  render(<App />);
  const heading = screen.getByText(/AI Code Mentor/i);
  expect(heading).toBeInTheDocument();
});
