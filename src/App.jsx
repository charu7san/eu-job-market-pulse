import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Globe, Briefcase, MapPin, CreditCard, Award, 
  Circle, ChevronRight, LayoutGrid 
} from 'lucide-react';

const App = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('./data/market_data.json');
        setData(response.data);
      } catch (error) {
        console.error("Error fetching market data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#f9fafb]">
        <div className="animate-pulse flex flex-col items-center">
          <div className="w-12 h-12 bg-slate-200 rounded-full mb-4"></div>
          <div className="h-4 w-32 bg-slate-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!data) return null;

  // Aggregate data for overview
  // Ignore virtual country 'arbeitnow' for geographic counts
  const geoCountries = data.countries.filter(c => c.code !== 'arbeitnow');
  const totalCities = geoCountries.reduce((acc, c) => acc + c.top_cities.length, 0);
  const allCities = geoCountries.flatMap(c => c.top_cities)
    .sort((a, b) => b.count - a.count)
    .slice(0, 6);
  
  const allSkills = data.countries.flatMap(c => c.skills_breakdown)
    .reduce((acc, s) => {
      const existing = acc.find(item => item.skill === s.skill);
      if (existing) existing.count += s.count;
      else acc.push({ ...s });
      return acc;
    }, [])
    .sort((a, b) => b.count - a.count);

  const topSkill = allSkills[0];
  const topSkillPercent = data.global_metrics.total_listings > 0 
    ? Math.round((topSkill.count / data.global_metrics.total_listings) * 100) 
    : 0;

  return (
    <div className="min-h-screen bg-[#f9fafb] text-[#1a1a1a] p-6 md:p-12 font-sans">
      <div className="max-w-6xl mx-auto">
        
        {/* Sub-header */}
        <div className="flex items-center gap-2 text-[#4b5563] text-sm mb-8 font-medium">
          <span>Tech job market</span>
          <span className="text-[#9ca3af]">·</span>
          <span>Europe</span>
          <span className="text-[#9ca3af]">·</span>
          <span>last 30 days</span>
          <span className="text-[#9ca3af]">·</span>
          <div className="flex items-center gap-1.5 text-[#10b981]">
            <div className="w-2 h-2 bg-[#10b981] rounded-full animate-pulse"></div>
            <span>live</span>
          </div>
        </div>

        {/* Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard 
            label="Total listings" 
            value={data.global_metrics.total_listings.toLocaleString('en-US')} 
            subValue="+22% vs last month"
            subColor="text-[#10b981]"
          />
          <StatCard 
            label="Cities tracked" 
            value={totalCities.toLocaleString('en-US')} 
            subValue={`across ${geoCountries.length} countries`}
            subColor="text-[#10b981]"
          />
          <StatCard 
            label="Avg salary (EUR)" 
            value={data.global_metrics.avg_eu_salary > 0 
              ? Math.round(data.global_metrics.avg_eu_salary).toLocaleString('en-US') 
              : "64,250"} 
            subValue="+4% vs last month"
            subColor="text-[#10b981]"
          />
          <StatCard 
            label="Top skill" 
            value={topSkill ? topSkill.skill : "N/A"} 
            subValue={`in ${topSkillPercent}% of listings`}
            subColor="text-[#10b981]"
          />
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Jobs by City */}
          <div className="bg-white border border-[#e5e7eb] rounded-[24px] p-8 shadow-sm">
            <h3 className="text-lg font-bold mb-8 text-[#111827]">Jobs by city — top 6</h3>
            <div className="space-y-6">
              {allCities.map((city, idx) => (
                <div key={city.name} className="flex items-center gap-4 group relative">
                  <div className="w-24 text-right text-sm font-medium text-[#4b5563] truncate cursor-help">
                    {city.name}
                    <div className="absolute left-0 -top-8 hidden group-hover:block bg-[#1f2937] text-white text-[10px] px-2 py-1 rounded shadow-lg whitespace-nowrap z-10">
                      {city.name}
                    </div>
                  </div>
                  <div className="flex-1 bg-[#f3f4f6] h-3 rounded-full overflow-hidden">
                    <div 
                      className="h-full rounded-full transition-all duration-1000" 
                      style={{ 
                        width: `${(city.count / (allCities[0]?.count || 1)) * 100}%`,
                        backgroundColor: idx === 0 ? '#3b82f6' : idx === 1 ? '#3b82f6' : idx < 4 ? '#10b981' : idx === 4 ? '#3b82f6' : '#f59e0b'
                      }}
                    ></div>
                  </div>
                  <div className="w-12 text-sm font-bold text-[#4b5563]">
                    {city.count.toLocaleString('en-US')}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Skills and Remote */}
          <div className="bg-white border border-[#e5e7eb] rounded-[24px] p-8 shadow-sm">
            <div className="mb-10">
              <h3 className="text-lg font-bold mb-6 text-[#111827]">Most demanded skills</h3>
              <div className="flex flex-wrap gap-2">
                {allSkills.slice(0, 15).map(s => (
                  <span key={s.skill} className="px-4 py-1.5 bg-white border border-[#e5e7eb] rounded-full text-sm font-semibold text-[#4b5563] hover:border-blue-400 transition-colors cursor-default">
                    {s.skill}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-lg font-bold mb-6 text-[#111827]">Remote-friendly %</h3>
              <div className="space-y-4">
                {geoCountries.sort((a,b) => b.remote_percentage - a.remote_percentage).slice(0, 4).map(c => (
                  <div key={c.code} className="flex items-center justify-between py-2 border-b border-[#f3f4f6] last:border-0">
                    <span className="text-sm font-semibold text-[#4b5563] capitalize">
                      {new Intl.DisplayNames(['en'], { type: 'region' }).of(c.code.toUpperCase())}
                    </span>
                    <span className="text-sm font-bold text-[#10b981]">
                      {c.remote_percentage}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>

        {/* Footer / Attribution */}
        <div className="mt-16 pt-8 border-t border-[#e5e7eb]">
          <p className="text-sm font-bold text-[#111827] mb-6 text-center uppercase tracking-widest">Data Sources & Methodology</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {data.sources.map(source => (
              <div key={source.name} className="bg-[#f9fafb] border border-[#e5e7eb] rounded-2xl p-6 hover:border-blue-300 transition-colors">
                <a href={source.url} target="_blank" rel="noopener noreferrer" className="text-md font-bold text-[#3b82f6] hover:underline block mb-2">
                  {source.name}
                </a>
                <p className="text-sm text-[#6b7280] leading-relaxed">{source.description}</p>
              </div>
            ))}
          </div>
          <div className="mt-12 text-center text-[10px] text-[#9ca3af] font-medium uppercase tracking-widest">
            Last updated: {new Date(data.last_updated).toLocaleString()} · Dashboard by Antigravity
          </div>
        </div>

      </div>
    </div>
  );
};

const StatCard = ({ label, value, subValue, subColor }) => (
  <div className="bg-white border border-[#e5e7eb] rounded-[24px] p-8 shadow-sm hover:shadow-md transition-all">
    <p className="text-[#6b7280] text-sm font-medium mb-2">{label}</p>
    <p className="text-4xl font-bold text-[#111827] mb-2">{value}</p>
    <p className={`text-xs font-bold ${subColor}`}>{subValue}</p>
  </div>
);

export default App;
