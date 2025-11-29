export default function HowItWorksStep({ step, title, text }) {
  return (
    <div className="bg-white rounded-2xl shadow-md border p-5">
      <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-semibold mb-2">
        {step}
      </div>
      <h4 className="font-semibold mb-1">{title}</h4>
      <p className="text-sm text-gray-600">{text}</p>
    </div>
  );
}
