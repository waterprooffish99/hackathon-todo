/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Ensure Webpack mode is used (not Turbopack)
  experimental: {
    // Explicitly disable turbopack
  },

  webpack: (config, { dev, isServer }) => {
    // Add any necessary webpack configurations here
    if (dev && !isServer) {
      // Enable fast refresh in development
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      };
    }

    return config;
  },
};

module.exports = nextConfig;
