import TvlChart from "./components/TvlChart";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-100 p-6 space-y-6">
      <h1 className="text-3xl font-bold text-center text-blue-600">DADA – Cardano Risk Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <TvlChart protocol="Minswap" />
        <TvlChart protocol="Indigo" />
        #<TvlChart protocol="Liqwid" />
      </div>
    </div>
  );
}
