import { useTranslation } from 'react-i18next';

import { ErrorRow } from '@/components/ErrorRow';
import { useHealth } from '@/hooks/useHealth';

/** Renders nothing while the server is healthy or loading; a single error row otherwise. */
export function ServerStatus() {
  const { t } = useTranslation();
  const { isError, data, refetch, isFetching } = useHealth();

  if (!isError && data?.status !== 'degraded') return null;

  return (
    <ErrorRow
      message={t('errors.serverUnreachable')}
      onRetry={() => void refetch()}
      retrying={isFetching}
    />
  );
}
