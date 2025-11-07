"use client";

import { FormEvent, useState } from "react";
import { cancelOrderAction } from "../_lib/actions";
import Button from "./Button";

function CancelOrderBtn({ orderId }: { orderId: string }) {
  const [error, setError] = useState<string | null>(null);

  async function handleCancelOrder(e: FormEvent) {
    e.preventDefault();
    try {
      await cancelOrderAction(orderId);
    } catch (error) {
      if (error instanceof Error && error.message !== "NEXT_REDIRECT") {
        setError("Order could not be canceled.");
      }
    }
  }

  return (
    <form onSubmit={handleCancelOrder}>
      <Button type="primary">Cancel order</Button>
      {error && <p className="text-sm text-red-600">{error}</p>}
    </form>
  );
}

export default CancelOrderBtn;
