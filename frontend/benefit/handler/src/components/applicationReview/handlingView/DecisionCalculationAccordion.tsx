import {
  $CalculatorContainer,
  $DecisionCalculatorAccordion, $DecisionCalculatorAccordionIconContainer,
  $Section
} from 'benefit/handler/components/applicationReview/handlingView/DecisionCalculationAccordion.sc';
import { CALCULATION_PER_MONTH_ROW_TYPES } from 'benefit/handler/constants';
import { extractCalculatorRows, groupCalculatorRows } from 'benefit/handler/utils/calculator';
import { CALCULATION_ROW_DESCRIPTION_TYPES, CALCULATION_ROW_TYPES, } from 'benefit-shared/constants';
import { Application } from 'benefit-shared/types/application';
import { Accordion, IconGlyphEuro } from 'hds-react';
import { useTranslation } from 'next-i18next';
import * as React from 'react';
import { $ViewField } from 'shared/components/benefit/summaryView/SummaryView.sc';
import { $GridCell } from 'shared/components/forms/section/FormSection.sc';
import { formatFloatToCurrency } from 'shared/utils/string.utils';
import { useTheme } from 'styled-components';

import { $CalculatorTableHeader, $CalculatorTableRow, $Highlight, } from '../ApplicationReview.sc';

type Props = {
  data: Application;
}

const DecisionCalculationAccordion: React.FC<Props> = ({
                                                    data,
                                                  }) => {
  const theme = useTheme();
  const translationsBase = 'common:calculators.result';
  const { t } = useTranslation();
  const { rowsWithoutTotal, totalRow, totalRowDescription } =
    extractCalculatorRows(data?.calculation?.rows);

  // Group rows into sections to give monthly subtotals a separate background color
  const sections = groupCalculatorRows(rowsWithoutTotal);

  const headingSize = { fontSize: theme.fontSize.heading.l };

  return (<$DecisionCalculatorAccordion>
      <$DecisionCalculatorAccordionIconContainer aria-hidden="true">
        <IconGlyphEuro />
      </$DecisionCalculatorAccordionIconContainer>
      <Accordion
    heading={t(
      'common:applications.decision.calculation'
    )}
    card
    size="s">
      <$GridCell
        $colSpan={11}
        style={{
          padding: theme.spacing.m
        }}
      >
        <$CalculatorContainer>
          {totalRow && (
            <>
              <$CalculatorTableHeader css={headingSize}>
                {t(`${translationsBase}.header`)}
              </$CalculatorTableHeader>
              <$Highlight data-testid="calculation-results-total">
                <div style={{ fontSize: theme.fontSize.body.xl }}>
                  {totalRowDescription
                    ? totalRowDescription.descriptionFi
                    : totalRow?.descriptionFi}
                </div>
                <div style={{ fontSize: theme.fontSize.heading.xl }}>
                  {formatFloatToCurrency(totalRow.amount, 'EUR', 'fi-FI', 0)}
                </div>
              </$Highlight>
              <hr style={{ margin: theme.spacing.s }} />
            </>
          )}
          <$CalculatorTableHeader style={{ paddingBottom: theme.spacing.m }} css={headingSize}>
            {t(`${translationsBase}.header2`)}
          </$CalculatorTableHeader>
          {sections.map((section) => {
            const firstRowIsMonthSubtotal = [
              CALCULATION_ROW_TYPES.HELSINKI_BENEFIT_MONTHLY_EUR,
              CALCULATION_ROW_TYPES.HELSINKI_BENEFIT_SUB_TOTAL_EUR
            ].includes(section[0]?.rowType);

            return <$Section key={section[0].id || 'filler'} className={firstRowIsMonthSubtotal ? 'subtotal' : ''}>{section.map((row) => {
              const isDateRange =
                CALCULATION_ROW_DESCRIPTION_TYPES.DATE === row.descriptionType;
              const isDescriptionRowType =
                CALCULATION_ROW_TYPES.DESCRIPTION === row.rowType;

              const isPerMonth = CALCULATION_PER_MONTH_ROW_TYPES.includes(
                row.rowType
              );
              return (
                <div key={row.id}>
                  {CALCULATION_ROW_TYPES.HELSINKI_BENEFIT_MONTHLY_EUR ===
                    row.rowType && (
                      <$CalculatorTableRow>
                        <$ViewField isBold>
                          {t(`${translationsBase}.acceptedBenefit`)}
                        </$ViewField>
                      </$CalculatorTableRow>
                    )}
                  <$CalculatorTableRow
                    isNewSection={isDateRange}
                    style={{
                      marginBottom: '7px',
                    }}
                  >
                    <$ViewField
                      isBold={isDateRange || isDescriptionRowType}
                      isBig={isDateRange}
                    >
                      {row.descriptionFi}
                    </$ViewField>
                    {!isDescriptionRowType && (
                      <$ViewField
                        isBold
                        style={{ marginRight: theme.spacing.xl4 }}
                      >
                        {formatFloatToCurrency(row.amount)}
                        {isPerMonth && t('common:utility.perMonth')}
                      </$ViewField>
                    )}
                  </$CalculatorTableRow>
                </div>
              );
            })}</$Section>;
          })}
        </$CalculatorContainer>
      </$GridCell>
    </Accordion></$DecisionCalculatorAccordion>
  );
};

export default DecisionCalculationAccordion;
