/**
 * Error Formatting and Diagnostic Explanations for Spatial Analytics (Stage 131).
 */

export function formatSpatialAnalyticsErrorMessage(errorCode: string, defaultMessage?: string): string {
  switch (errorCode) {
    case 'INVALID_H3_CELL':
      return 'The specified H3 hexagonal cell identifier is malformed or invalid.';
    case 'INVALID_H3_RESOLUTION':
      return 'The requested H3 resolution level is outside permitted limits (0 to 15).';
    case 'EXCESSIVE_H3_RESOLUTION':
      return 'The requested resolution would exceed safe viewport query bounds. Please zoom in before increasing resolution.';
    case 'UNAUTHORIZED_SPATIAL_DATASET':
      return 'Access to this proprietary analytical spatial dataset is restricted under your organization policy.';
    case 'SPATIAL_METRIC_NOT_ALLOWED':
      return 'The chosen aggregation function is mathematically invalid or disallowed for this metric.';
    case 'PRIVACY_SUPPRESSED':
      return 'Detailed observations for this cell are protected by minimum-contributor privacy suppression.';
    case 'SOURCE_ENTITLEMENT_REVOKED':
      return 'Source licensing for this dataset has expired or was revoked. Derived aggregates are unavailable.';
    case 'SPATIAL_QUERY_TIMEOUT':
      return 'The spatial analytics calculation timed out. Try applying a smaller viewport or coarser resolution.';
    default:
      return defaultMessage || 'An unexpected spatial analytics error occurred.';
  }
}

