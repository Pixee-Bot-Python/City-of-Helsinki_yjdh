import { Selector } from 'testcafe';

import MainIngress from './MainIngress';
import Step1 from './step1';
import Step2 from './step2';

export type DeMinimisRow = {
  granter: string;
  amount: string;
  grantedAt: string;
};

export enum SAVE_ACTIONS {
  CONTINUE = 'continue',
  SAVE_AND_EXIT = 'saveAndExit',
}
class DeMinimisAid {
  public step1: Step1;

  public step2: Step2;

  public t: TestController;

  private deminimisRowSelector = '[data-testid="deminimis-row"]';

  fillMandatoryFields = async (): Promise<void> => {
    const mainIngress = new MainIngress();
    await mainIngress.isLoaded();
    await mainIngress.clickCreateNewApplicationButton();

    await this.step1.isLoaded(30_000);

    await this.step1.fillEmployerInfo('6051437344779954', false);
    await this.step1.fillContactPerson(
      'Tester',
      'Example',
      '050001234',
      'tester@example.com'
    );
    await this.step1.selectNocoOperationNegotiations();
  };

  public getRowCount = async (): Promise<number> =>
    Selector(this.deminimisRowSelector).count;

  private step1ToStep2 = async (): Promise<void> => {
    await this.step1.clickSubmit();
    await this.step2.isLoaded();
  };

  private step2ToStep1 = async (): Promise<void> => {
    await this.step2.clickPrevious();
    await this.step1.isLoaded();
  };

  public saveExitAndEdit = async (t: TestController): Promise<void> => {
    await this.step1.clickSaveAndClose();
    const mainIngress = new MainIngress();
    await mainIngress.isLoaded();
    await t.click(Selector('[data-testid="application-edit-button"]'));
    await this.step1.isLoaded();
    await t.scrollIntoView(Selector('button').withText('Jatka'));
  };

  public actions = {
    saveStep1AndReturn: async (): Promise<void> => {
      await this.step1ToStep2();
      await this.step2ToStep1();
    },
    fillRows: async (
      t: TestController,
      rows: DeMinimisRow[],
      action?: SAVE_ACTIONS
    ): Promise<void> => {
      // eslint-disable-next-line no-restricted-syntax
      for (const row of rows) {
        // eslint-disable-next-line no-await-in-loop
        await this.step1.fillDeminimisAid(
          row.granter,
          row.amount,
          row.grantedAt
        );
      }
      if (action === SAVE_ACTIONS.CONTINUE) {
        await this.actions.saveStep1AndReturn();
        await t.scrollIntoView(Selector('button').withText('Jatka'));
        await t.expect(await this.getRowCount()).eql(rows.length);
      }
      if (action === SAVE_ACTIONS.SAVE_AND_EXIT) {
        await this.saveExitAndEdit(t);
        await t.expect(await this.getRowCount()).eql(rows.length);
      }
    },

    removeRow: async (index: number): Promise<void> =>
      this.step1.clickDeminimisRemove(index),

    removeAllRows: async (rows: DeMinimisRow[]): Promise<void> => {
      // eslint-disable-next-line no-restricted-syntax, @typescript-eslint/no-unused-vars
      for (const _ of rows) {
        // eslint-disable-next-line no-await-in-loop
        await this.step1.clickDeminimisRemove(0);
      }
    },

    fillTooBigAmounts: async (t: TestController): Promise<void> => {
      const rows = [
        { granter: 'One', amount: '2', grantedAt: '1.1.2023' },
        { granter: 'Two', amount: '199999', grantedAt: '2.2.2023' },
      ];
      await this.actions.fillRows(t, rows);

      const deminimisMaxError = Selector(
        '[data-testid="deminimis-maxed-notification"]'
      );
      await t.expect(await deminimisMaxError.exists).ok();
      await this.step1.expectSubmitDisabled();

      await this.actions.removeAllRows(rows);

      await t.expect(await this.getRowCount()).eql(0);
    },

    fillAndLeaveUnfinished: async (t: TestController): Promise<void> => {
      await this.step1.fillDeminimisAid('One', '1', '');
      await this.step1.clickSubmit();
      const toastError = Selector(
        '.Toastify__toast-body[role="alert"]'
      ).withText('Puuttuvia de minimis-tuen tietoja');
      await t.expect(await toastError.exists).ok();
      await t.click(toastError.find('[title="Sulje ilmoitus"]'));
    },

    clearRowsWithSelectNo: async (
      t: TestController,
      action: SAVE_ACTIONS
    ): Promise<void> => {
      await this.step1.selectNoDeMinimis();

      if (action === SAVE_ACTIONS.CONTINUE) {
        await this.actions.saveStep1AndReturn();
      }
      if (action === SAVE_ACTIONS.SAVE_AND_EXIT) {
        await this.saveExitAndEdit(t);
      }

      await this.step1.selectYesDeMinimis();
      await t.scrollIntoView(Selector('button').withText('Jatka'));
      await t.expect(await this.getRowCount()).eql(0);
    },
  };

  constructor(t: TestController, step1: Step1, step2: Step2) {
    this.t = t;
    this.step1 = step1;
    this.step2 = step2;
  }
}
export default DeMinimisAid;
