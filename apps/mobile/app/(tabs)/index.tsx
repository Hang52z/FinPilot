import { ServerStatus } from '@/components/ServerStatus';
import { Screen } from '@/components/Screen';

export default function HomeScreen() {
  return (
    <Screen>
      <ServerStatus />
    </Screen>
  );
}
