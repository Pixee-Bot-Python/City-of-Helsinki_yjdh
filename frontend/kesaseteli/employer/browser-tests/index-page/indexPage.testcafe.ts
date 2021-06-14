import { HttpRequestHook } from '@frontend/shared/browser-tests/hooks/http-request-hook';
import isRealIntegrationsEnabled from '@frontend/shared/browser-tests/utils/is-real-integrations-enabled';
import { clearDataToPrintOnFailure } from '@frontend/shared/browser-tests/utils/testcafe.utils';
import TestController from 'testcafe';

import { doEmployerLogin } from '../actions/employer-header.actions';
import { getPageLayoutComponents } from '../common-components/pageLayout.components';
import { getEmployerUiUrl } from '../utils/settings';
import { getIndexPageComponents } from './indexPage.components';

let indexPageComponents: ReturnType<typeof getIndexPageComponents>;
let pageLayoutComponents: ReturnType<typeof getPageLayoutComponents>;

const url = getEmployerUiUrl('/');

fixture('Frontpage')
  .page(url)
  .requestHooks(new HttpRequestHook(url))
  .beforeEach(async (t) => {
    clearDataToPrintOnFailure(t);
    indexPageComponents = getIndexPageComponents(t);
    pageLayoutComponents = getPageLayoutComponents(t);
  });

test('user can authenticate and logout', async (t: TestController) => {
  const expectations = await doEmployerLogin(t);
  const indexPageHeader = await indexPageComponents.header();
  if (isRealIntegrationsEnabled() && expectations) {
    await indexPageHeader.expectations.userNameIsPresent(
      expectations.expectedUser
    );
  }
  await indexPageHeader.actions.clickLogoutButton();
  const loginHeader = await pageLayoutComponents.header();
  await loginHeader.expectations.loginButtonIsPresent();
});
