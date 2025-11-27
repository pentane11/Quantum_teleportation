# 本リポジトリでは、量子テレポーテーション実験(シミュレーション・実機実装)に使用したソースコードを格納する。

動作環境 (Requirements)
本プロジェクトは以下のライブラリを使用しています。
Python 3.x
qiskit >= 1.0.0
qiskit-aer
qiskit-ibm-runtime
matplotlib

ファイル構成 (Files)
1. Quantum_teleportation_simulation.py
   シミュレーターを用いた実験コードです。
   100,000ショットのサンプリングによる量子トモグラフィを実行します。
2. Quantum_teleportation_machine.py
   実機（IBM Quantum）で実行するためのコードです。
   QiskitRuntimeService を使用し、SamplerV2を用いて実機へジョブを送信します。
