import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Empty turbopack config to silence webpack/turbopack conflict warning
  // Turbopack is the default bundler in Next.js 16
  turbopack: {},
  
  // Externalize packages that have issues with bundling (e.g., test files)
  serverExternalPackages: ['pino', 'thread-stream', 'pino-pretty'],
  
  webpack: (config) => {
    // Ignore test files from node_modules to prevent bundling dev dependencies
    config.plugins.push(
      new (require('webpack').IgnorePlugin)({
        resourceRegExp: /\/(test|tests|__tests__)\//,
        contextRegExp: /node_modules/,
      })
    );
    
    return config;
  },
};

export default nextConfig;
