// src/app.d.ts

/// <reference types="svelte" />

// Declare missing svelteHTML namespace for event typings like on:load
declare namespace svelteHTML {
  interface HTMLAttributes<T> {
    // for on:load, on:focus, etc.
    [key: `on${string}`]: (event: any) => void;
  }
}
