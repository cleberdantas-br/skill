import { Button, Badge, Codicon, useValue } from '@hermes/plugin-sdk';
import { jsx } from 'react/jsx-runtime';

const ID = 'checkout-assist';

function CheckoutAssistPane({ host }) {
  const busy = useValue(host.state.busy);
  const openBrowser = async () => {
    const result = await host.runAction('view.showBrowser');
    host.notify({ kind: result.ok ? 'info' : 'error', message: result.ok ? 'Browser panel opened.' : 'Browser panel is unavailable.' });
  };
  return jsx('div', {
    style: { padding: '12px', display: 'flex', flexDirection: 'column', gap: '10px', color: 'var(--ui-text-secondary)' },
    children: [
      jsx('div', { style: { display: 'flex', alignItems: 'center', gap: '8px' }, children: [jsx(Codicon, { name: 'shopping-cart' }), jsx('strong', { style: { color: 'var(--ui-text-primary)' }, children: 'Checkout Assist' })] }),
      jsx('div', { children: 'Acompanhamento de compra com navegador visível e Playwright. O agente prepara o carrinho e para antes de login, 2FA e pagamento.' }),
      jsx('div', { style: { display: 'flex', alignItems: 'center', gap: '8px' }, children: [jsx(Badge, { children: busy ? 'Agente trabalhando' : 'Pronto para iniciar' })] }),
      jsx(Button, { onClick: openBrowser, children: 'Abrir painel de navegador' }),
      jsx('div', { style: { fontSize: '12px', color: 'var(--ui-text-quaternary)' }, children: 'Peça: “iniciar Checkout Assist com <URL>”. O navegador visível usa um perfil local isolado.' }),
    ],
  });
}

export default {
  id: ID,
  name: 'Checkout Assist',
  defaultEnabled: false,
  register(ctx) {
    ctx.register({
      id: 'checkout-pane',
      area: 'panes',
      data: { title: 'Checkout Assist', placement: 'right', width: '320px' },
      render: () => jsx(CheckoutAssistPane, { host: ctx.host }),
    });
    ctx.register({
      id: 'open-browser',
      area: 'palette',
      data: { label: 'Checkout Assist: abrir painel de navegador', onSelect: () => ctx.runAction('view.showBrowser') },
    });
  },
};
