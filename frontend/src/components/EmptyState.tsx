import { Button } from './ui/button';

interface EmptyStateProps {
  icon: string;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export const EmptyState = ({ icon, title, description, action }: EmptyStateProps) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <div className="text-6xl mb-4" aria-hidden="true">{icon}</div>
      <h3 className="text-xl font-semibold mb-2 text-text">{title}</h3>
      <p className="text-text-muted mb-6 max-w-md">{description}</p>
      {action && (
        <Button onClick={action.onClick} variant="default">
          {action.label}
        </Button>
      )}
    </div>
  );
};
