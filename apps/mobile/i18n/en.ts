const en = {
  tabs: {
    home: 'Home',
    research: 'Research',
    ai: 'AI',
    portfolio: 'Portfolio',
  },
  settings: {
    title: 'Settings',
    language: 'Language',
  },
  watchlist: {
    empty: 'No symbols',
    search: 'Search',
    add: 'Add to watchlist',
    remove: 'Remove from watchlist',
  },
  search: {
    placeholder: 'Search',
    noResults: 'No results',
    etf: 'ETF',
  },
  market: {
    dailyClose: 'Daily close · {{date}} · {{source}}',
    noPrices: 'No price data',
    ranges: {
      '1M': '1M',
      '3M': '3M',
      '6M': '6M',
      '1Y': '1Y',
      '5Y': '5Y',
    },
  },
  errors: {
    serverUnreachable: "Can't reach server",
    symbolNotFound: 'Symbol not found',
    dataUnavailable: 'Market data unavailable',
    quotaExceeded: 'Data limit reached. Try again later.',
    generic: 'Something went wrong',
    retry: 'Retry',
  },
};

export default en;
export type Translation = typeof en;
