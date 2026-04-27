> [!NOTE]
> 이 문서는 AI 에이전트(Gemini CLI, Claude 등)가 cmux-win 프로젝트를 구현하고 검증하는 데 참고하는 핵심 지침서입니다.
# 02. 肄붿뼱 ??(?덈룄?? 硫붿떆吏 猷⑦봽, ?쇱씠?꾩궗?댄겢)

> [!IMPORTANT]
> ?꾩옱 ??μ냼?먯꽌 ?ㅼ젣濡?議댁옱?섎뒗 援ы쁽? `cmux/Sources/`??macOS Swift 肄붾뱶?낅땲?? ??臾몄꽌???섏삤??`App.xaml / App.xaml.cpp`, `MainWindow.xaml / .cpp`, `WindowManager.h/cpp`??**WinUI 3 (Windows App SDK) 湲곕컲 紐⑺몴 ?ㅺ퀎**?대ŉ ?꾩쭅 ??μ냼???놁뒿?덈떎.

## cmux ?먮낯 (macOS)

| ?뚯씪 | ??븷 |
|------|------|
| `cmuxApp.swift` | @main SwiftUI App, ?섍꼍 珥덇린?? StateObject ?앹꽦 |
| `AppDelegate.swift` | NSApplicationDelegate, ???앸챸二쇨린, 湲濡쒕쾶 ?대깽???몃뱾留?|
| `ContentView.swift` | 猷⑦듃 酉? NSGlassEffectView / NSVisualEffectView |
| `WindowToolbarController.swift` | NSToolbar 愿由?|
| `WindowDecorationsController.swift` | ?몃옒???쇱씠??踰꾪듉 愿由?|

## cmux-win 紐⑺몴 ?ㅺ퀎 (WinUI 3 ?섏씠釉뚮━??

WinUI 3??XAML 而댄룷吏???몃━瑜??꾩엯?섏뿬 ?덈룄???댁쓽 紐⑤뱺 UI ?붿냼瑜??듯빀 ?뚮뜑留곹빀?덈떎. 湲곗〈 Win32 HWND ?먯떇 李쎈뱾??以묒꺽?쇰줈 ?명빐 諛쒖깮?????덉뿀??**?먯뼱?ㅽ럹?댁뒪(Airspace) 諛?Z-order 臾몄젣瑜??먯쿇?곸쑝濡??닿껐**?⑸땲??

### ?꾩옱 援ы쁽 湲곗? vs 紐⑺몴 ?ㅺ퀎

| 援щ텇 | ?꾩옱 援ы쁽 (`cmux/`) | 紐⑺몴 ?ㅺ퀎 (`cmux-win`) |
|------|----------------------|-------------------------|
| ??吏꾩엯??| `cmuxApp.swift`, `AppDelegate.swift` | WinUI 3 Bootstrap + `App.xaml` |
| ?덈룄???꾨젅??| `ContentView.swift` + AppKit | `MainWindow.xaml` + WinUI 3 Window |
| 硫붿떆吏 猷⑦봽 | GCD / RunLoop | WinUI 3 `Application::Start` + `DispatcherQueue` |
| COM 珥덇린??| N/A | **`COINIT_APARTMENTTHREADED` (STA)** |

---

### App.xaml / App.xaml.cpp

```
??븷: WinUI 3 吏꾩엯?? ?좏뵆由ъ??댁뀡 ?쇱씠?꾩궗?댄겢, 湲濡쒕쾶 由ъ냼??XAML) 愿由?
??? cmuxApp.swift + AppDelegate.swift
```

**二쇱슂 湲곕뒫 諛?蹂寃쎌젏**:
- **COM 珥덇린??*: WinUI 3, XAML ?명봽?? WebView2, ?대┰蹂대뱶, ?쒕옒洹????쒕∼ ?깆쓽 ?뺤긽 ?묐룞???꾪빐 **`COINIT_APARTMENTTHREADED` (STA)** ?ㅻ젅??紐⑤뜽??媛뺤젣?⑸땲?? 湲곗〈 `COINIT_MULTITHREADED` (MTA) 湲곕컲 ?ㅺ퀎??XAML怨??명솚?섏? ?딆쑝誘濡??먭린?⑸땲??
- **硫붿떆吏 猷⑦봽**: 湲곗〈 Win32 `GetMessage` 湲곕컲 而ㅼ뒪? 硫붿떆吏 猷⑦봽 ??? `Microsoft::UI::Xaml::Application::Start` ?대? 硫붿떆吏 猷⑦봽? `DispatcherQueue` ?대깽??紐⑤뜽???곕쫭?덈떎.
- 湲濡쒕쾶 XAML 由ъ냼???뚮쭏, 湲곕낯 ?ㅽ??? 釉뚮윭?? 濡쒕뱶 諛????꾩뿭 ?ㅼ젙 珥덇린??

**?덉긽 珥덇린???쒖꽌(?ㅺ퀎 ?쒖븞)**:
```cpp
#include <windows.h>
#include <winrt/Windows.Foundation.h>
#include <winrt/Microsoft.UI.Xaml.h>

int __stdcall wWinMain(HINSTANCE, HINSTANCE, PWSTR, int) {
    // WinUI 3瑜??꾪븳 COM STA 珥덇린??(?꾩닔)
    winrt::init_apartment(winrt::apartment_type::single_threaded);
    
    // Windows App SDK Bootstrap 珥덇린??(MSIX ?⑦궎吏??щ????곕씪 遺꾧린)
    ::MddBootstrapInitialize2(...);
    
    // WinUI 3 ???쒖옉 (?대??곸쑝濡?硫붿떆吏 猷⑦봽 諛??덈룄???꾨줈?쒖? ?ㅽ뻾)
    ::winrt::Microsoft::UI::Xaml::Application::Start([](auto&&) {
        ::winrt::make<::winrt::cmux::implementation::App>();
    });
    
    ::MddBootstrapShutdown();
    return 0;
}
```

**?앸챸二쇨린 ?대깽??*:
| macOS | Windows (WinUI 3) |
|-------|---------|
| `applicationDidFinishLaunching` | `App::OnLaunched` |
| `applicationWillTerminate` | Window `Closed` ?대깽??+ `Application::UnhandledException` 泥섎━ |
| suspend / resume | `App::OnSuspending` / `App::OnResuming` (?⑦궎吏 ???먮뒗 OS ?섎챸二쇨린 ?섏〈) |
| `applicationDidBecomeActive` | Window `Activated` (WindowActivationState != Deactivated) |
| `applicationDidResignActive` | Window `Activated` (WindowActivationState == Deactivated) |

---

### MainWindow.xaml / MainWindow.xaml.cpp

```
??븷: 硫붿씤 ?덈룄???꾨젅?? XAML 而댄룷吏???몃━ 援ъ꽦, ?덉씠?꾩썐 愿由?
??? ContentView.swift + WindowToolbarController.swift
```

**二쇱슂 湲곕뒫**:
- **XAML ?듯빀 UI**: ?ъ씠?쒕컮, ?덉씠?꾩썐 遺꾪븷湲?SplitView/Grid), ?⑤꼸(?곕??? 釉뚮씪?곗?), 寃???ㅻ쾭?덉씠 ?깆쓣 ?⑥씪 XAML ?몃━濡?援ъ꽦?⑸땲??
- **?섏씠釉뚮━???곕????몄뒪??*: ?곕??먯? ?쒖닔 HWND媛 ?꾨땶 XAML `SwapChainPanel`???듯빐 ?몄뒪?낅맗?덈떎. ?대? ?듯빐 ?곕????꾩뿉 寃?됱갹怨?媛숈? XAML 而⑦듃濡ㅼ쓣 ?먯돺寃??щ┫ ???덉뒿?덈떎.
- **?⑤꼸 ?쇱슦??*: `MainWindow`???뚰겕?ㅽ럹?댁뒪???섎굹??`PanelContainer`瑜??몄뒪?명븯怨? 媛?`PanelContainer` ?대??먯꽌 `TerminalPanel` ?먮뒗 `BrowserPanel` UserControl code-behind媛 `IPanel` ?명꽣?섏씠?ㅻ? 援ы쁽?⑸땲??
- **Mica / Acrylic ?④낵**: WinUI 3 `SystemBackdrop` API瑜??ъ슜?섏뿬 Windows 11??Mica ?④낵 諛?Windows 10??Acrylic ?④낵瑜??곸슜?⑸땲??
- **而ㅼ뒪? ??댄?諛?*: `AppWindow.TitleBar.ExtendsContentIntoTitleBar = true` ?띿꽦???ъ슜?섏뿬 ??댄?諛붾? ?④린怨??쒕옒洹?媛???곸뿭??而ㅼ뒪? XAML ?붿냼濡??泥댄빀?덈떎.

**?덉씠?꾩썐 援ъ“ (XAML 湲곕컲 ?쒖븞)**:
```xml
<Window
    x:Class="cmux.MainWindow"
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    xmlns:local="using:cmux.Panels">
    
    <Grid>
        <!-- 而ㅼ뒪? ??댄?諛??곸뿭 -->
        <Grid x:Name="AppTitleBar" Height="32" VerticalAlignment="Top" />
        
        <!-- 硫붿씤 ?덉씠?꾩썐 -->
        <SplitView DisplayMode="Inline" IsPaneOpen="True" Margin="0,32,0,0">
            <SplitView.Pane>
                <!-- ?ъ씠?쒕컮 (??紐⑸줉, ?뚮┝ ?곹깭) -->
            </SplitView.Pane>
            <SplitView.Content>
                <!-- ?뚰겕?ㅽ럹?댁뒪 而⑦뀗痢??곸뿭 -->
                <Grid>
                    <!-- ?쒖꽦 ?⑤꼸(?곕???釉뚮씪?곗?)???쇱슦?낇븯??XAML ?몄뒪??-->
                    <local:PanelContainer />
                </Grid>
            </SplitView.Content>
        </SplitView>
    </Grid>
</Window>
```

---

### WindowManager.h/cpp

```
??븷: 硫???덈룄???앹꽦/愿由??ъ빱??
??? AppDelegate.swift???덈룄??愿由?遺遺?
```

**二쇱슂 湲곕뒫**:
- WinUI 3 `Window` ?몄뒪?댁뒪?ㅼ쓽 ?쇱씠?꾩궗?댄겢 諛?紐⑸줉 愿由?
- ???덈룄???앹꽦 (Ctrl+Shift+N ?⑥텞???쇱슦??.
- ?꾩옱 ?쒖꽦?붾맂 ?덈룄??異붿쟻 諛?留덉?留??덈룄?곌? ?ロ옄 ??`Application.Exit()` ?몄텧.

---

## ?듭떖 WinUI 3 / WinRT API 留ㅽ븨

| macOS (AppKit/SwiftUI) | Windows (WinUI 3 / WinRT) |
|------------------------|-----------------|
| `NSApplication.shared` | `Microsoft::UI::Xaml::Application::Current()` |
| `NSWindow` | `Microsoft::UI::Xaml::Window` |
| `NSView` | `Microsoft::UI::Xaml::UIElement` / `FrameworkElement` |
| `NSGlassEffectView` | `MicaBackdrop` (`SystemBackdrop`) |
| `NSVisualEffectView` | `DesktopAcrylicBackdrop` |
| `NSToolbar` (而ㅼ뒪? 罹≪뀡) | `AppWindow.TitleBar.ExtendsContentIntoTitleBar` |
| `@Published` | `INotifyPropertyChanged` ?명꽣?섏씠??|
| `DispatchQueue.main` | `DispatcherQueue` |
| Metal + IOSurface | **`SwapChainPanel` + Direct2D/DirectWrite** |

### AI ?먯씠?꾪듃??蹂댁씪?ы뵆?덉씠??(App.xaml.h)

```cpp
#pragma once
#include "App.xaml.g.h"

namespace winrt::cmux::implementation
{
    struct App : AppT<App>
    {
        App();
        void OnLaunched(Microsoft::UI::Xaml::LaunchActivatedEventArgs const&);
    private:
        winrt::Microsoft::UI::Xaml::Window m_window{ nullptr };
    };
}
```

### AI ?먯씠?꾪듃 ?ㅽ뻾 泥댄겕由ъ뒪??

- [ ] **Bootstrap 珥덇린??*: `MddBootstrapInitialize2`媛 `wWinMain` 理쒖긽?⑥뿉???몄텧?섎뒗媛?
- [ ] **STA Apartment**: `winrt::init_apartment(winrt::apartment_type::single_threaded)`媛 ?좎뼵?섏뿀?붽??
- [ ] **Mica ?쒖꽦??*: `MainWindow` ?앹꽦 ??`SystemBackdrop` ?ㅼ젙 濡쒖쭅???ы븿?섏뿀?붽??
- [ ] **??댄?諛?而ㅼ뒪?**: `ExtendsContentIntoTitleBar`媛 true濡??ㅼ젙?섍퀬 `SetTitleBar` ?몄텧???꾨즺?섏뿀?붽??
- [ ] **由ъ냼???ъ쟾 濡쒕뱶**: `App.xaml`???뺤쓽??湲濡쒕쾶 ?ㅽ???釉뚮윭?쒓? ?고??꾩뿉 ?뺤긽 濡쒕뱶?섎뒗媛?

