function InputErrorMessage({ children }: { children: React.ReactNode }) {
  return <span className="text-sm text-red-600">{children}</span>;
}

export default InputErrorMessage;
