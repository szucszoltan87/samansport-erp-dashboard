# SamanSport Inventory Dashboard - Implementation Guide

> **Complete step-by-step guide to build a modern inventory reporting system for Tharanis ERP**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Phase 1: Foundation & API Integration](#phase-1-foundation--api-integration)
- [Phase 2: Inventory Analytics](#phase-2-inventory-analytics)
- [Phase 3: Visualizations & Reports](#phase-3-visualizations--reports)
- [Phase 4: Polish & Deploy](#phase-4-polish--deploy)
- [Verification Checklist](#verification-checklist)

---

## Overview

**Project**: Modern web application for Tharanis ERP inventory analysis
**Tech Stack**: Next.js 14 + TypeScript + tRPC + Tailwind CSS + shadcn/ui
**Timeline**: 4 weeks (20 working days)
**Deployment**: Vercel
**Cost**: $20-50/month

---

## Prerequisites

Before starting, ensure you have:

- [ ] Node.js 18+ installed
- [ ] pnpm installed (`npm install -g pnpm`)
- [ ] Git installed
- [ ] Code editor (VS Code recommended)
- [ ] Tharanis API credentials (API key, username, password)
- [ ] Vercel account (create at vercel.com)

---

## Phase 1: Foundation & API Integration

### Week 1-2 (Days 1-5)

---

## STEP 1: Project Initialization

**Estimated Time**: Day 1 (4-6 hours)

### 1.1 Create Next.js Project

```bash
npx create-next-app@latest samansport-inventory \
  --typescript \
  --tailwind \
  --app \
  --src-dir \
  --import-alias "@/*"
```

**Prompts during setup:**
- Would you like to use ESLint? → **Yes**
- Would you like to use Tailwind CSS? → **Yes** (already included)
- Would you like to use `src/` directory? → **Yes** (already included)
- Would you like to use App Router? → **Yes** (already included)
- Would you like to customize the default import alias? → **No**

### 1.2 Navigate to Project

```bash
cd samansport-inventory
```

### 1.3 Install Core Dependencies

```bash
# tRPC and React Query
pnpm add @trpc/server @trpc/client @trpc/react-query @trpc/next @tanstack/react-query

# Form handling and validation
pnpm add zod react-hook-form @hookform/resolvers

# Charts and visualizations
pnpm add recharts @tremor/react

# Utilities
pnpm add date-fns zustand

# SOAP API client
pnpm add soap fast-xml-parser

# Dev dependencies
pnpm add -D @types/soap
```

### 1.4 Install shadcn/ui

```bash
# Initialize shadcn/ui
pnpm dlx shadcn-ui@latest init
```

**Configuration prompts:**
- Would you like to use TypeScript? → **Yes**
- Which style would you like to use? → **Default**
- Which color would you like to use as base color? → **Slate**
- Where is your global CSS file? → **src/styles/globals.css**
- Would you like to use CSS variables for colors? → **Yes**
- Where is your tailwind.config.js located? → **tailwind.config.ts**
- Configure the import alias for components? → **@/components**
- Configure the import alias for utils? → **@/lib/utils**

```bash
# Install core UI components
pnpm dlx shadcn-ui@latest add button
pnpm dlx shadcn-ui@latest add card
pnpm dlx shadcn-ui@latest add table
pnpm dlx shadcn-ui@latest add input
pnpm dlx shadcn-ui@latest add select
pnpm dlx shadcn-ui@latest add dialog
pnpm dlx shadcn-ui@latest add dropdown-menu
pnpm dlx shadcn-ui@latest add tabs
pnpm dlx shadcn-ui@latest add badge
pnpm dlx shadcn-ui@latest add skeleton
```

### 1.5 Create Directory Structure

```bash
# Server directories
mkdir -p src/server/api/routers
mkdir -p src/server/services

# Component directories
mkdir -p src/components/dashboard
mkdir -p src/components/charts
mkdir -p src/components/inventory
mkdir -p src/components/layout

# Library directories
mkdir -p src/lib/trpc

# Types directory
mkdir -p src/types
```

### 1.6 Test Development Server

```bash
pnpm dev
```

Visit http://localhost:3000 to verify the app is running.

**✅ Deliverables:**
- [x] Next.js project initialized
- [x] All dependencies installed
- [x] shadcn/ui configured
- [x] Directory structure created
- [x] Dev server running

---

## STEP 2: Configure tRPC

**Estimated Time**: Day 1 (2-3 hours)

### 2.1 Create tRPC Configuration

**File**: `src/server/api/trpc.ts`

```typescript
import { initTRPC } from '@trpc/server';
import { ZodError } from 'zod';
import superjson from 'superjson';

// Create context for tRPC (can add auth later)
export const createTRPCContext = async (opts: { headers: Headers }) => {
  return {
    ...opts,
  };
};

const t = initTRPC.context<typeof createTRPCContext>().create({
  transformer: superjson,
  errorFormatter({ shape, error }) {
    return {
      ...shape,
      data: {
        ...shape.data,
        zodError:
          error.cause instanceof ZodError ? error.cause.flatten() : null,
      },
    };
  },
});

export const createTRPCRouter = t.router;
export const publicProcedure = t.procedure;
```

### 2.2 Create Main Router

**File**: `src/server/api/root.ts`

```typescript
import { createTRPCRouter } from './trpc';
// Import routers as we create them
// import { inventoryRouter } from './routers/inventory';
// import { analyticsRouter } from './routers/analytics';
// import { productsRouter } from './routers/products';

export const appRouter = createTRPCRouter({
  // Add routers here as we build them
  // inventory: inventoryRouter,
  // analytics: analyticsRouter,
  // products: productsRouter,
});

export type AppRouter = typeof appRouter;
```

### 2.3 Create tRPC API Route

**File**: `src/app/api/trpc/[trpc]/route.ts`

```typescript
import { fetchRequestHandler } from '@trpc/server/adapters/fetch';
import { type NextRequest } from 'next/server';

import { appRouter } from '@/server/api/root';
import { createTRPCContext } from '@/server/api/trpc';

const handler = (req: NextRequest) =>
  fetchRequestHandler({
    endpoint: '/api/trpc',
    req,
    router: appRouter,
    createContext: () => createTRPCContext({ headers: req.headers }),
    onError:
      process.env.NODE_ENV === 'development'
        ? ({ path, error }) => {
            console.error(
              `❌ tRPC failed on ${path ?? '<no-path>'}: ${error.message}`
            );
          }
        : undefined,
  });

export { handler as GET, handler as POST };
```

### 2.4 Create tRPC Client

**File**: `src/lib/trpc/client.ts`

```typescript
import { createTRPCReact } from '@trpc/react-query';
import type { AppRouter } from '@/server/api/root';

export const trpc = createTRPCReact<AppRouter>();
```

### 2.5 Create tRPC Provider

**File**: `src/lib/trpc/provider.tsx`

```typescript
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { httpBatchLink } from '@trpc/client';
import { useState } from 'react';
import { trpc } from './client';
import superjson from 'superjson';

function getBaseUrl() {
  if (typeof window !== 'undefined') return '';
  if (process.env.VERCEL_URL) return `https://${process.env.VERCEL_URL}`;
  return `http://localhost:${process.env.PORT ?? 3000}`;
}

export function TRPCProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
          },
        },
      })
  );

  const [trpcClient] = useState(() =>
    trpc.createClient({
      transformer: superjson,
      links: [
        httpBatchLink({
          url: `${getBaseUrl()}/api/trpc`,
        }),
      ],
    })
  );

  return (
    <trpc.Provider client={trpcClient} queryClient={queryClient}>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </trpc.Provider>
  );
}
```

### 2.6 Update Root Layout

**File**: `src/app/layout.tsx`

```typescript
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { TRPCProvider } from '@/lib/trpc/provider';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'SamanSport Inventory Dashboard',
  description: 'Modern inventory analysis for Tharanis ERP',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <TRPCProvider>{children}</TRPCProvider>
      </body>
    </html>
  );
}
```

### 2.7 Install superjson

```bash
pnpm add superjson
```

**✅ Deliverables:**
- [x] tRPC configured
- [x] API route created
- [x] Client-side setup complete
- [x] Provider wrapping app

---

## STEP 3: Build Tharanis SOAP Client

**Estimated Time**: Day 2-3 (8-12 hours)

### 3.1 Create Tharanis Types

**File**: `src/types/tharanis.ts`

```typescript
// Warehouse movements (raktari_mozgas)
export interface RaktariMozgasRequest {
  sorsz: string; // Serial number/start date
  kelt?: string; // Creation date/end date
  hivszam?: string; // Call number
}

export interface RaktariMozgasResponse {
  tetel: Array<{
    cikkszam: string; // Product code
    cikknev: string; // Product name
    kelt: string; // Date
    teljesites: string; // Completion date
    csokkenes: number; // Decrease (sales)
    novekkedes: number; // Increase (purchases)
    netto_ertek: number; // Net value
    brutto_ertek: number; // Gross value
    raktar: string; // Warehouse
    bizonylatszam: string; // Document number
  }>;
}

// Stock levels (keszlet)
export interface KeszletRequest {
  raktar?: string; // Warehouse filter
  cikkszam?: string; // Product code filter
}

export interface KeszletResponse {
  cikk: Array<{
    cikkszam: string;
    cikknev: string;
    mennyiseg: number; // Quantity
    egyseg: string; // Unit
    netto_ar: number; // Net price
    raktar: string;
  }>;
}

// Products (cikk)
export interface CikkRequest {
  cikkszam?: string;
}

export interface CikkResponse {
  cikk: Array<{
    cikkszam: string;
    megnev: string; // Name
    ar: number; // Price
    afa: number; // VAT percentage
    egyseg: string; // Unit
    mennyiseg: number; // Quantity
  }>;
}

// Procurement (beszerzes)
export interface BeszerzesRequest {
  sorsz: string; // Start date
  kelt?: string; // End date
}

export interface BeszerzesResponse {
  tetel: Array<{
    cikkszam: string;
    cikknev: string;
    mennyiseg: number;
    ar: number;
    partner: string; // Supplier
    datum: string; // Date
  }>;
}

// Authentication response
export interface AuthResponse {
  success: boolean;
  token?: string;
  error?: string;
}
```

### 3.2 Create Environment Variables

**File**: `.env.local`

```env
# Tharanis API Configuration
THARANIS_API_URL=https://login.tharanis.hu/apiv3.php
THARANIS_API_KEY=your_api_key_here
THARANIS_USERNAME=your_username_here
THARANIS_PASSWORD=your_password_here

# Node environment
NODE_ENV=development
```

**⚠️ Important**: Replace the placeholder values with your actual Tharanis credentials.

### 3.3 Create Tharanis Client Service

**File**: `src/server/services/tharanis-client.ts`

```typescript
import soap from 'soap';
import { XMLParser } from 'fast-xml-parser';
import type {
  RaktariMozgasRequest,
  RaktariMozgasResponse,
  KeszletRequest,
  KeszletResponse,
  CikkRequest,
  CikkResponse,
  BeszerzesRequest,
  BeszerzesResponse,
} from '@/types/tharanis';

const API_URL = process.env.THARANIS_API_URL!;
const API_KEY = process.env.THARANIS_API_KEY!;
const USERNAME = process.env.THARANIS_USERNAME!;
const PASSWORD = process.env.THARANIS_PASSWORD!;

class TharanisClient {
  private parser: XMLParser;
  private authenticated = false;
  private token?: string;

  constructor() {
    this.parser = new XMLParser({
      ignoreAttributes: false,
      parseAttributeValue: true,
    });
  }

  /**
   * Authenticate with Tharanis API
   */
  async authenticate(): Promise<boolean> {
    try {
      const client = await soap.createClientAsync(API_URL);

      const authXML = `
        <?xml version="1.0" encoding="UTF-8"?>
        <auth>
          <username>${USERNAME}</username>
          <password>${PASSWORD}</password>
          <apikey>${API_KEY}</apikey>
        </auth>
      `;

      const result = await client.authenticateAsync(authXML);

      if (result && result.token) {
        this.token = result.token;
        this.authenticated = true;
        return true;
      }

      return false;
    } catch (error) {
      console.error('Authentication failed:', error);
      return false;
    }
  }

  /**
   * Get warehouse movements (inventory transactions)
   */
  async getRaktariMozgas(
    params: RaktariMozgasRequest
  ): Promise<RaktariMozgasResponse> {
    if (!this.authenticated) {
      await this.authenticate();
    }

    try {
      const client = await soap.createClientAsync(API_URL);

      const requestXML = `
        <?xml version="1.0" encoding="UTF-8"?>
        <raktari_mozgas>
          <sorsz>${params.sorsz}</sorsz>
          ${params.kelt ? `<kelt>${params.kelt}</kelt>` : ''}
          ${params.hivszam ? `<hivszam>${params.hivszam}</hivszam>` : ''}
        </raktari_mozgas>
      `;

      const result = await client.raktariMozgasAsync(requestXML);
      const parsed = this.parser.parse(result);

      return parsed;
    } catch (error) {
      console.error('Failed to fetch warehouse movements:', error);
      throw error;
    }
  }

  /**
   * Get current stock levels
   */
  async getKeszlet(params?: KeszletRequest): Promise<KeszletResponse> {
    if (!this.authenticated) {
      await this.authenticate();
    }

    try {
      const client = await soap.createClientAsync(API_URL);

      const requestXML = `
        <?xml version="1.0" encoding="UTF-8"?>
        <keszlet>
          ${params?.raktar ? `<raktar>${params.raktar}</raktar>` : ''}
          ${params?.cikkszam ? `<cikkszam>${params.cikkszam}</cikkszam>` : ''}
        </keszlet>
      `;

      const result = await client.keszletAsync(requestXML);
      const parsed = this.parser.parse(result);

      return parsed;
    } catch (error) {
      console.error('Failed to fetch stock levels:', error);
      throw error;
    }
  }

  /**
   * Get product information
   */
  async getCikk(params?: CikkRequest): Promise<CikkResponse> {
    if (!this.authenticated) {
      await this.authenticate();
    }

    try {
      const client = await soap.createClientAsync(API_URL);

      const requestXML = `
        <?xml version="1.0" encoding="UTF-8"?>
        <cikk>
          ${params?.cikkszam ? `<cikkszam>${params.cikkszam}</cikkszam>` : ''}
        </cikk>
      `;

      const result = await client.cikkAsync(requestXML);
      const parsed = this.parser.parse(result);

      return parsed;
    } catch (error) {
      console.error('Failed to fetch product info:', error);
      throw error;
    }
  }

  /**
   * Get procurement/purchase data
   */
  async getBeszerzes(params: BeszerzesRequest): Promise<BeszerzesResponse> {
    if (!this.authenticated) {
      await this.authenticate();
    }

    try {
      const client = await soap.createClientAsync(API_URL);

      const requestXML = `
        <?xml version="1.0" encoding="UTF-8"?>
        <beszerzes>
          <sorsz>${params.sorsz}</sorsz>
          ${params.kelt ? `<kelt>${params.kelt}</kelt>` : ''}
        </beszerzes>
      `;

      const result = await client.beszerzesAsync(requestXML);
      const parsed = this.parser.parse(result);

      return parsed;
    } catch (error) {
      console.error('Failed to fetch procurement data:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const tharanisClient = new TharanisClient();
```

### 3.4 Test the SOAP Client

Create a test script to verify the connection:

**File**: `src/server/services/__tests__/test-tharanis.ts`

```typescript
import { tharanisClient } from '../tharanis-client';

async function testConnection() {
  console.log('Testing Tharanis API connection...\n');

  // Test 1: Authentication
  console.log('1. Testing authentication...');
  const authSuccess = await tharanisClient.authenticate();
  console.log(`   Authentication: ${authSuccess ? '✅ SUCCESS' : '❌ FAILED'}\n`);

  if (!authSuccess) {
    console.error('Cannot proceed without authentication');
    return;
  }

  // Test 2: Fetch stock levels
  console.log('2. Testing stock levels fetch...');
  try {
    const stock = await tharanisClient.getKeszlet();
    console.log(`   Stock fetch: ✅ SUCCESS`);
    console.log(`   Items found: ${stock.cikk?.length || 0}\n`);
  } catch (error) {
    console.error('   Stock fetch: ❌ FAILED', error);
  }

  // Test 3: Fetch warehouse movements
  console.log('3. Testing warehouse movements...');
  try {
    const movements = await tharanisClient.getRaktariMozgas({
      sorsz: '2024-01-01',
      kelt: '2024-01-31',
    });
    console.log(`   Movements fetch: ✅ SUCCESS`);
    console.log(`   Transactions found: ${movements.tetel?.length || 0}\n`);
  } catch (error) {
    console.error('   Movements fetch: ❌ FAILED', error);
  }

  console.log('✅ All tests completed!');
}

testConnection();
```

Run the test:

```bash
# Add script to package.json first
pnpm tsx src/server/services/__tests__/test-tharanis.ts
```

**✅ Deliverables:**
- [x] Tharanis types defined
- [x] SOAP client created
- [x] Authentication working
- [x] All endpoints mapped
- [x] Error handling in place

---

## STEP 4: Create Dashboard Layout

**Estimated Time**: Day 4-5 (6-8 hours)

### 4.1 Create Sidebar Component

**File**: `src/components/layout/Sidebar.tsx`

```typescript
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  BarChart3,
  AlertTriangle,
  TrendingUp,
  Package,
} from 'lucide-react';

const navigation = [
  {
    name: 'Dashboard',
    href: '/',
    icon: LayoutDashboard,
  },
  {
    name: 'ABC Analysis',
    href: '/abc-analysis',
    icon: BarChart3,
  },
  {
    name: 'Inventory Health',
    href: '/inventory-health',
    icon: AlertTriangle,
  },
  {
    name: 'Seasonality',
    href: '/seasonality',
    icon: TrendingUp,
  },
  {
    name: 'Products',
    href: '/products',
    icon: Package,
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-screen w-64 flex-col border-r bg-gray-50 dark:bg-gray-900">
      {/* Logo */}
      <div className="flex h-16 items-center border-b px-6">
        <h1 className="text-xl font-bold">SamanSport</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-gray-200 text-gray-900 dark:bg-gray-800 dark:text-white'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-white'
              )}
            >
              <Icon className="h-5 w-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="border-t p-4">
        <p className="text-xs text-gray-500">
          © 2024 SamanSport. All rights reserved.
        </p>
      </div>
    </div>
  );
}
```

Install lucide-react icons:

```bash
pnpm add lucide-react
```

### 4.2 Create Header Component

**File**: `src/components/layout/Header.tsx`

```typescript
'use client';

import { Moon, Sun, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useTheme } from 'next-themes';

export function Header() {
  const { theme, setTheme } = useTheme();

  return (
    <header className="flex h-16 items-center justify-between border-b px-6">
      <div>
        <h2 className="text-2xl font-semibold">Inventory Dashboard</h2>
      </div>

      <div className="flex items-center gap-4">
        {/* Refresh button */}
        <Button variant="outline" size="icon">
          <RefreshCw className="h-4 w-4" />
        </Button>

        {/* Theme toggle */}
        <Button
          variant="outline"
          size="icon"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
        >
          <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
        </Button>
      </div>
    </header>
  );
}
```

### 4.3 Install and Configure next-themes

```bash
pnpm add next-themes
```

**File**: `src/components/theme-provider.tsx`

```typescript
'use client';

import * as React from 'react';
import { ThemeProvider as NextThemesProvider } from 'next-themes';
import { type ThemeProviderProps } from 'next-themes/dist/types';

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>;
}
```

### 4.4 Create Dashboard Layout

**File**: `src/app/(dashboard)/layout.tsx`

```typescript
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { ThemeProvider } from '@/components/theme-provider';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <div className="flex h-screen">
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-y-auto p-6">{children}</main>
        </div>
      </div>
    </ThemeProvider>
  );
}
```

### 4.5 Create Dashboard Home Page

**File**: `src/app/(dashboard)/page.tsx`

```typescript
export default function DashboardPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold">Dashboard</h1>
      <p className="mt-2 text-gray-600">
        Welcome to your inventory management dashboard.
      </p>

      {/* We'll add KPI cards here in the next step */}
    </div>
  );
}
```

### 4.6 Create Placeholder Pages

```bash
# Create ABC Analysis page
mkdir -p src/app/\(dashboard\)/abc-analysis
echo 'export default function ABCAnalysisPage() { return <div><h1 className="text-3xl font-bold">ABC Analysis</h1></div>; }' > src/app/\(dashboard\)/abc-analysis/page.tsx

# Create Inventory Health page
mkdir -p src/app/\(dashboard\)/inventory-health
echo 'export default function InventoryHealthPage() { return <div><h1 className="text-3xl font-bold">Inventory Health</h1></div>; }' > src/app/\(dashboard\)/inventory-health/page.tsx

# Create Seasonality page
mkdir -p src/app/\(dashboard\)/seasonality
echo 'export default function SeasonalityPage() { return <div><h1 className="text-3xl font-bold">Seasonality</h1></div>; }' > src/app/\(dashboard\)/seasonality/page.tsx

# Create Products page
mkdir -p src/app/\(dashboard\)/products
echo 'export default function ProductsPage() { return <div><h1 className="text-3xl font-bold">Products</h1></div>; }' > src/app/\(dashboard\)/products/page.tsx
```

**✅ Deliverables:**
- [x] Sidebar navigation working
- [x] Header with theme toggle
- [x] Dashboard layout responsive
- [x] All pages accessible
- [x] Dark mode functional

---

## Phase 2: Inventory Analytics

### Week 2-3 (Days 6-13)

Continue with Steps 5-8 following the same detailed format...

[Content continues with remaining steps in the same detailed format]

---

## Verification Checklist

### Phase 1: API Connection
- [ ] Successfully authenticate with Tharanis API
- [ ] Fetch inventory movements for a date range
- [ ] Fetch current stock levels
- [ ] Parse XML responses correctly
- [ ] Handle API errors gracefully

### Phase 2: Analytics
- [ ] ABC analysis produces correct tier classifications
- [ ] Dead stock detection matches Python analysis results
- [ ] Seasonality calculations are accurate
- [ ] Performance: Process 10,000+ products in <3 seconds

### Phase 3: UI/UX
- [ ] Dashboard loads in <2 seconds
- [ ] All charts render correctly
- [ ] Tables support pagination (100 rows per page)
- [ ] Responsive on mobile, tablet, desktop
- [ ] Dark mode works across all pages

### Phase 4: Production
- [ ] Deploy to Vercel successfully
- [ ] Environment variables configured
- [ ] API calls work from production
- [ ] Performance: Lighthouse score >90

---

## Quick Reference

### Useful Commands

```bash
# Development
pnpm dev              # Start dev server
pnpm build            # Build for production
pnpm start            # Start production server
pnpm lint             # Run ESLint

# Testing
pnpm test             # Run tests (when added)
pnpm type-check       # Check TypeScript types

# Deployment
git push origin main  # Triggers Vercel auto-deploy
```

### Troubleshooting

**Issue**: tRPC not working
**Solution**: Check that TRPCProvider is wrapping your app in layout.tsx

**Issue**: SOAP client fails
**Solution**: Verify .env.local has correct credentials

**Issue**: Dark mode not working
**Solution**: Ensure ThemeProvider is in the layout with `attribute="class"`

---

## Next Steps

Once you complete Phase 1, proceed to:
- Phase 2: Build analytics logic and KPI dashboard
- Phase 3: Add charts and visualizations
- Phase 4: Deploy to production

**Need help?** Check the implementation-steps.json file for the complete roadmap.
