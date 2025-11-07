"use client";

import Button from "./Button";
import { FiFilter } from "react-icons/fi";
import { useFilterMenu } from "./FiltersContext";

function FiltersButton() {
  const { open } = useFilterMenu();

  return (
    <Button type="primary" onClick={open}>
      <FiFilter />
      Filters
    </Button>
  );
}

export default FiltersButton;
