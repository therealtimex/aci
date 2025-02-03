import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    domains: ["img.icons8.com"],
  },

  // TODO: directly sending requests to API URL right now
  // reenable rewrite after we switched to secure http cookie
  // for dev portal authentication

  // rewrite does not forward Authorization header, so it 
  // doesn't work with bearer token auth
  // rewrites: async () => {
  //   return [
  //     {
  //       source: "/v1/:path*",
  //       destination: `${process.env.API_URL}/v1/:path*`,
  //     },
  //   ];
  // },
};

export default nextConfig;
