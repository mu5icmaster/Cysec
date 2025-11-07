"use client";

import { createContext, ReactNode, useContext, useState } from "react";

interface FiltersMenuContextType {
  isOpen: boolean;
  open: () => void;
  close: () => void;
}

const FiltersMenuContext = createContext<FiltersMenuContextType>({
  isOpen: false,
  open: () => {},
  close: () => {},
});

function FiltersMenuProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);

  function open() {
    setIsOpen(true);
  }

  function close() {
    setIsOpen(false);
  }

  return (
    <FiltersMenuContext.Provider value={{ isOpen, open, close }}>
      {children}
    </FiltersMenuContext.Provider>
  );
}

function useFilterMenu() {
  const context = useContext(FiltersMenuContext);

  if (context === undefined)
    throw new Error("Filters menu context was used outside of its scope.");

  return context;
}

export { FiltersMenuProvider, useFilterMenu };
