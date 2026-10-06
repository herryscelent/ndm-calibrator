import type { ReactNode } from "react";

interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: ReactNode;
}

/** Standard page header: title + one-line description + optional actions. */
export function PageHeader({ title, description, actions }: PageHeaderProps) {
  return (
    <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 className="text-[22px] font-semibold leading-tight text-text-primary">
          {title}
        </h1>
        {description ? (
          <p className="mt-1 text-[13px] text-text-secondary">{description}</p>
        ) : null}
      </div>
      {actions ? <div className="flex max-w-full shrink-0 flex-wrap items-center gap-2">{actions}</div> : null}
    </div>
  );
}
