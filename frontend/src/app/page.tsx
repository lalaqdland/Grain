import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          {/* Logo和标题 */}
          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent">
            Grain
          </h1>
          <p className="text-2xl text-gray-600 mb-2">守拙</p>
          <p className="text-lg text-gray-500 mb-12">
            The AI Humanizer & Academic Shield
          </p>

          {/* 功能介绍 */}
          <div className="grid md:grid-cols-2 gap-8 mb-12">
            <div className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-shadow">
              <div className="text-4xl mb-4">🔴</div>
              <h3 className="text-xl font-bold mb-2">降重模式</h3>
              <p className="text-gray-600">
                针对知网、Turnitin标红段落，通过学术化扩写和结构重组，有效降低查重率
              </p>
            </div>
            <div className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-shadow">
              <div className="text-4xl mb-4">🟠</div>
              <h3 className="text-xl font-bold mb-2">降AI模式</h3>
              <p className="text-gray-600">
                针对GPTZero、Turnitin AI检测，通过熵增和人性化改写，让文本更自然
              </p>
            </div>
          </div>

          {/* 核心特性 */}
          <div className="bg-white p-8 rounded-2xl shadow-lg mb-12">
            <h2 className="text-2xl font-bold mb-6">核心特性</h2>
            <div className="grid md:grid-cols-3 gap-6 text-left">
              <div>
                <h4 className="font-bold mb-2">📄 格式神圣</h4>
                <p className="text-sm text-gray-600">
                  XML骨架置换技术，确保修改后格式分毫不差
                </p>
              </div>
              <div>
                <h4 className="font-bold mb-2">🖥️ 外屏协同</h4>
                <p className="text-sm text-gray-600">
                  配合系统分屏，专注极致编辑体验
                </p>
              </div>
              <div>
                <h4 className="font-bold mb-2">🤖 双模引擎</h4>
                <p className="text-sm text-gray-600">
                  降重与降AI两套算法，一键切换
                </p>
              </div>
            </div>
          </div>

          {/* CTA按钮 */}
          <Link
            href="/editor"
            className="inline-block bg-gradient-to-r from-blue-600 to-green-600 text-white px-12 py-4 rounded-full text-lg font-bold hover:shadow-2xl transition-all transform hover:scale-105"
          >
            开始使用 →
          </Link>

          {/* 版本信息 */}
          <p className="mt-12 text-sm text-gray-400">
            Version 3.1.0 (Local MVP) | Made with ❤️
          </p>
        </div>
      </div>
    </main>
  )
}

