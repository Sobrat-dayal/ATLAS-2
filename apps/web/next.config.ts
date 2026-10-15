import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async redirects() {
    return [
      {
        source: '/',
        destination: '/home',
        permanent: true,
      },
      // Legacy route migrations
      {
        source: '/screener',
        destination: '/screeners',
        permanent: true,
      },
      {
        source: '/economy',
        destination: '/economics',
        permanent: true,
      },
      {
        source: '/map',
        destination: '/maps',
        permanent: true,
      },
      {
        source: '/portfolio',
        destination: '/portfolios',
        permanent: true,
      },
      {
        source: '/analytics',
        destination: '/risk',
        permanent: true,
      }
    ];
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/api/:path*',
      },
    ];
  },
};

export default nextConfig;
