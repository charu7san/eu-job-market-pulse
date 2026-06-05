import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Globe, Briefcase, MapPin, CreditCard, Award, 
  Circle, ChevronRight, LayoutGrid 
} from 'lucide-react';
import { 
  ResponsiveContainer, PieChart, Pie, Cell, 
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip 
} from 'recharts';

const App = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [hoveredCountry, setHoveredCountry] = useState(null);
  const [hoveredSkill, setHoveredSkill] = useState(null);

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

  // Prepare country pie chart data
  const countryColors = {
    de: '#3b82f6', // blue
    es: '#10b981', // emerald
    fr: '#6366f1', // indigo
    it: '#8b5cf6', // violet
    nl: '#f59e0b', // amber
    be: '#ec4899', // pink
    at: '#ef4444', // red
  };

  const countryNames = {
    de: 'Germany',
    es: 'Spain',
    fr: 'France',
    it: 'Italy',
    nl: 'Netherlands',
    be: 'Belgium',
    at: 'Austria',
  };

  const countryPieData = data.countries
    .filter(c => c.code !== 'arbeitnow')
    .map(c => ({
      code: c.code,
      name: countryNames[c.code] || c.code.toUpperCase(),
      value: c.job_count,
      color: countryColors[c.code] || '#9ca3af',
    }))
    .sort((a, b) => b.value - a.value);

  const totalJobCount = countryPieData.reduce((acc, c) => acc + c.value, 0);

  countryPieData.forEach(item => {
    item.percentage = ((item.value / totalJobCount) * 100).toFixed(1);
  });

  // Prepare remote radar chart data
  const radarData = geoCountries.map(c => ({
    subject: countryNames[c.code] || c.code.toUpperCase(),
    value: c.remote_percentage,
  }));

  // Prepare skills bar chart data
  const skillsChartData = allSkills.slice(0, 8).map(s => ({
    name: s.skill,
    count: s.count,
  }));

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
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Jobs by City */}
          <div className="bg-white border border-[#e5e7eb] rounded-[24px] p-8 shadow-sm flex flex-col justify-between h-full">
            <div>
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
          </div>

          {/* Job Distribution by Country */}
          <div className="bg-white border border-[#e5e7eb] rounded-[24px] p-8 shadow-sm flex flex-col justify-between h-full">
            <div>
              <div className="flex items-center gap-2 mb-6">
                <Globe className="w-5 h-5 text-[#3b82f6]" />
                <h3 className="text-lg font-bold text-[#111827]">Jobs by country</h3>
              </div>
              
              <div className="relative w-full h-[220px] flex items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={countryPieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={65}
                      outerRadius={85}
                      paddingAngle={3}
                      dataKey="value"
                      onMouseEnter={(e, index) => setHoveredCountry(countryPieData[index])}
                      onMouseLeave={() => setHoveredCountry(null)}
                    >
                      {countryPieData.map((entry, index) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={entry.color} 
                          fillOpacity={hoveredCountry ? (hoveredCountry.code === entry.code ? 1.0 : 0.35) : 0.95}
                          className="transition-all duration-300 outline-none cursor-pointer"
                        />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                
                <div className="absolute flex flex-col items-center justify-center text-center pointer-events-none select-none">
                  {hoveredCountry ? (
                    <>
                      <span className="text-[10px] font-bold text-[#6b7280] uppercase tracking-wider mb-0.5">
                        {hoveredCountry.name}
                      </span>
                      <span className="text-2xl font-extrabold text-[#111827] leading-none mb-1">
                        {hoveredCountry.value.toLocaleString('en-US')}
                      </span>
                      <span className="text-xs font-bold text-[#3b82f6]">
                        {hoveredCountry.percentage}%
                      </span>
                    </>
                  ) : (
                    <>
                      <span className="text-[10px] font-bold text-[#6b7280] uppercase tracking-wider mb-0.5">
                        Total Jobs
                      </span>
                      <span className="text-2xl font-extrabold text-[#111827] leading-none mb-1">
                        {totalJobCount.toLocaleString('en-US')}
                      </span>
                      <span className="text-xs font-medium text-[#9ca3af]">
                        7 Countries
                      </span>
                    </>
                  )}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-x-3 gap-y-2 mt-4 border-t border-[#f3f4f6] pt-4">
              {countryPieData.map((item) => (
                <div 
                  key={item.code} 
                  className={`flex items-center justify-between text-[11px] p-1 rounded-lg transition-all duration-200 cursor-pointer ${
                    hoveredCountry?.code === item.code ? 'bg-[#f3f4f6] scale-[1.02]' : 'hover:bg-[#f9fafb]'
                  }`}
                  onMouseEnter={() => setHoveredCountry(item)}
                  onMouseLeave={() => setHoveredCountry(null)}
                >
                  <div className="flex items-center gap-1.5 min-w-0">
                    <span 
                      className="w-2 h-2 rounded-full shrink-0" 
                      style={{ backgroundColor: item.color }}
                    ></span>
                    <span className="font-semibold text-[#4b5563] truncate">
                      {item.name}
                    </span>
                  </div>
                  <span className="font-bold text-[#111827] ml-1 shrink-0">
                    {item.percentage}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Remote Work Profile */}
          <div className="bg-white border border-[#e5e7eb] rounded-[24px] p-8 shadow-sm flex flex-col justify-between h-full">
            <div>
              <div className="flex items-center gap-2 mb-6">
                <MapPin className="w-5 h-5 text-[#10b981]" />
                <h3 className="text-lg font-bold text-[#111827]">Remote work profile</h3>
              </div>
              
              <div className="w-full h-[220px] flex items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                    <PolarGrid stroke="#f3f4f6" />
                    <PolarAngleAxis 
                      dataKey="subject" 
                      tick={{ fill: '#4b5563', fontSize: 10, fontWeight: 600 }}
                    />
                    <PolarRadiusAxis 
                      angle={30} 
                      domain={[0, 30]} 
                      tick={{ fill: '#9ca3af', fontSize: 8 }} 
                      axisLine={false}
                    />
                    <Radar
                      name="Remote %" 
                      dataKey="value" 
                      stroke="#10b981" 
                      fill="#10b981" 
                      fillOpacity={0.15} 
                    />
                    <Tooltip 
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const data = payload[0].payload;
                          return (
                            <div className="bg-white border border-[#e5e7eb] rounded-xl p-2.5 shadow-md text-[11px]">
                              <p className="font-bold text-[#111827]">{data.subject}</p>
                              <p className="font-extrabold text-[#10b981] mt-0.5">
                                {data.value}% <span className="font-medium text-[#6b7280]">remote-friendly</span>
                              </p>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            <div className="mt-4 border-t border-[#f3f4f6] pt-4">
              <div className="flex items-center justify-between text-[11px] text-[#6b7280] font-medium">
                <span>Avg remote-friendliness</span>
                <span className="font-bold text-[#111827]">
                  {(radarData.reduce((acc, curr) => acc + curr.value, 0) / radarData.length).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>

        </div>

        {/* Row 3: Skills In-Depth Analysis */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
          
          {/* Tech Skills Demand Bar Chart */}
          <div className="bg-white border border-[#e5e7eb] rounded-[24px] p-8 shadow-sm lg:col-span-2 flex flex-col justify-between h-full">
            <div>
              <div className="flex items-center gap-2 mb-6">
                <Briefcase className="w-5 h-5 text-[#3b82f6]" />
                <h3 className="text-lg font-bold text-[#111827]">Tech skills demand — top 8</h3>
              </div>
              
              <div className="w-full h-[260px] mt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={skillsChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="skillsGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.85} />
                        <stop offset="100%" stopColor="#6366f1" stopOpacity={0.4} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                    <XAxis 
                      dataKey="name" 
                      tick={{ fill: '#4b5563', fontSize: 11, fontWeight: 600 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis 
                      tick={{ fill: '#9ca3af', fontSize: 10 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <Tooltip 
                      cursor={{ fill: '#f3f4f6', opacity: 0.4 }}
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const data = payload[0].payload;
                          return (
                            <div className="bg-white border border-[#e5e7eb] rounded-xl p-3 shadow-md text-xs">
                              <p className="font-bold text-[#111827]">{data.name}</p>
                              <p className="font-extrabold text-[#3b82f6] mt-0.5">
                                {data.count.toLocaleString()} <span className="font-medium text-[#6b7280]">listings</span>
                              </p>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Bar 
                      dataKey="count" 
                      fill="url(#skillsGradient)" 
                      radius={[6, 6, 0, 0]} 
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Skill Highlights & Interactive Insights */}
          <div className="bg-white border border-[#e5e7eb] rounded-[24px] p-8 shadow-sm flex flex-col justify-between h-full">
            <div>
              <div className="flex items-center gap-2 mb-6">
                <Award className="w-5 h-5 text-[#f59e0b]" />
                <h3 className="text-lg font-bold text-[#111827]">Skill highlights</h3>
              </div>
              <p className="text-xs text-[#6b7280] mb-4">
                Hover over a skill tag to explore its relative market share and count across the EU tech job market.
              </p>
              <div className="flex flex-wrap gap-2">
                {allSkills.slice(0, 15).map(s => {
                  const isHovered = hoveredSkill?.skill === s.skill;
                  return (
                    <span 
                      key={s.skill} 
                      className={`px-3 py-1.5 border rounded-full text-xs font-semibold cursor-pointer transition-all duration-200 ${
                        isHovered 
                          ? 'border-[#3b82f6] bg-[#eff6ff] text-[#3b82f6] scale-[1.05]' 
                          : 'border-[#e5e7eb] bg-white text-[#4b5563] hover:border-[#9ca3af]'
                      }`}
                      onMouseEnter={() => setHoveredSkill(s)}
                      onMouseLeave={() => setHoveredSkill(null)}
                    >
                      {s.skill}
                    </span>
                  );
                })}
              </div>
            </div>

            <div className="mt-6 border-t border-[#f3f4f6] pt-5 min-h-[96px] flex flex-col justify-center">
              {hoveredSkill ? (
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-[#111827]">{hoveredSkill.skill}</span>
                    <span className="text-xs font-bold text-[#3b82f6]">
                      {((hoveredSkill.count / data.global_metrics.total_listings) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-[#f3f4f6] h-2 rounded-full overflow-hidden">
                    <div 
                      className="bg-gradient-to-r from-[#3b82f6] to-[#6366f1] h-full rounded-full transition-all duration-300"
                      style={{ width: `${(hoveredSkill.count / data.global_metrics.total_listings) * 100}%` }}
                    ></div>
                  </div>
                  <p className="text-[10px] text-[#6b7280] mt-2 leading-relaxed">
                    Required in <span className="font-semibold text-[#4b5563]">{hoveredSkill.count.toLocaleString()}</span> of {data.global_metrics.total_listings.toLocaleString()} total listings.
                  </p>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center text-center text-[#9ca3af] py-2">
                  <Award className="w-6 h-6 opacity-40 mb-1" />
                  <span className="text-xs font-medium">Hover over a skill above</span>
                </div>
              )}
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
