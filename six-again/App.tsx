import { StatusBar } from 'expo-status-bar';
import { createElement } from 'react';
import { Platform, StyleSheet, View } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { WebView } from 'react-native-webview';

import { GAME_HTML } from './game/gameHtml';

// The whole game is one self-contained HTML file (see web/index.html). The app shows it full screen.
// A fixed https base URL gives the page a stable origin, so its localStorage saves survive app restarts.
const BASE_URL = 'https://six-again.app/';

export default function App() {
  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.root} edges={['top', 'bottom']}>
        <StatusBar style="light" />
        {Platform.OS === 'web' ? (
          <View style={styles.root}>
            {createElement('iframe', { srcDoc: GAME_HTML, title: '6 Again', style: { border: 0, width: '100%', height: '100%' } })}
          </View>
        ) : (
          <WebView
            style={styles.root}
            originWhitelist={['*']}
            source={{ html: GAME_HTML, baseUrl: BASE_URL }}
            domStorageEnabled
            javaScriptEnabled
            setSupportMultipleWindows={false}
            allowsBackForwardNavigationGestures={false}
            overScrollMode="never"
            textZoom={100}
          />
        )}
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#12213b' },
});
