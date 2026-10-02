import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

const String apiUrl = "https://agrotech-api-ldyv.onrender.com/api";

void main() {
  runApp(const AgroTechApp());
}

class AgroTechApp extends StatelessWidget {
  const AgroTechApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AgroTech Intelligence',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0B0F19),
        primaryColor: const Color(0xFF10B981),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF10B981),
          secondary: Color(0xFF38BDF8),
          surface: Color(0xFF111827),
        ),
      ),
      home: const LoginScreen(),
    );
  }
}

// ----------------- LOGIN -----------------
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _senhaController = TextEditingController();
  bool _isLoading = false;

  Future<void> _entrar() async {
    final email = _emailController.text.trim();
    final senha = _senhaController.text.trim();

    if (email.isEmpty || senha.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Preencha o e-mail e a palavra-passe.')),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      final response = await http.post(
        Uri.parse('$apiUrl/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"email": email, "senha": senha}),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        final role = data['role'] ?? 'user';
        final uid = data['uid'];
        final nome = data['nome'] ?? 'Produtor';

        if (!mounted) return;
        if (role == 'admin') {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (_) => AdminScreen(uid: uid)),
          );
        } else {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (_) => ProducerScreen(uid: uid, nome: nome)),
          );
        }
      } else {
        throw Exception(data['detail'] ?? 'Erro ao entrar');
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro: $e')),
      );
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Image.asset('assets/logo.png', height: 80, width: 80, fit: BoxFit.contain),
              const SizedBox(height: 10),
              const Text(
                'AgroTech Intelligence',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF10B981)),
              ),
              const SizedBox(height: 30),
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: const Color(0xFF111827),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFF374151)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Iniciar Sessão', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 14),
                    TextField(
                      controller: _emailController,
                      decoration: InputDecoration(
                        labelText: 'E-mail',
                        filled: true,
                        fillColor: const Color(0xFF1F2937),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _senhaController,
                      obscureText: true,
                      decoration: InputDecoration(
                        labelText: 'Palavra-passe',
                        filled: true,
                        fillColor: const Color(0xFF1F2937),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                    ),
                    const SizedBox(height: 20),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF10B981),
                          foregroundColor: Colors.black,
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                        onPressed: _isLoading ? null : _entrar,
                        child: _isLoading 
                          ? const CircularProgressIndicator(color: Colors.black)
                          : const Text('Entrar', style: TextStyle(fontWeight: FontWeight.bold)),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Center(
                      child: TextButton(
                        onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const RegisterScreen())),
                        child: const Text('Não tem conta? Criar Registo', style: TextStyle(color: Color(0xFF38BDF8))),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ----------------- REGISTO -----------------
class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _nomeController = TextEditingController();
  final _emailController = TextEditingController();
  final _senhaController = TextEditingController();
  bool _isLoading = false;

  Future<void> _registar() async {
    final nome = _nomeController.text.trim();
    final email = _emailController.text.trim();
    final senha = _senhaController.text.trim();

    if (nome.isEmpty || email.isEmpty || senha.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Preencha todos os campos.')));
      return;
    }

    setState(() => _isLoading = true);
    try {
      final response = await http.post(
        Uri.parse('$apiUrl/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"nome": nome, "email": email, "senha": senha}),
      );

      Map<String, dynamic> data = {};
      try {
        data = jsonDecode(response.body);
      } catch (_) {
        data = {"detail": response.body};
      }

      if (response.statusCode == 200 || response.statusCode == 201) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(data['message'] ?? 'Conta criada com sucesso!')),
        );
        Navigator.pop(context);
      } else {
        throw Exception(data['detail'] ?? 'Erro ao registar (Código: ${response.statusCode})');
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro: $e')));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Criar Nova Conta')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            TextField(controller: _nomeController, decoration: const InputDecoration(labelText: 'Nome Completo')),
            const SizedBox(height: 12),
            TextField(controller: _emailController, decoration: const InputDecoration(labelText: 'E-mail')),
            const SizedBox(height: 12),
            TextField(controller: _senhaController, obscureText: true, decoration: const InputDecoration(labelText: 'Palavra-passe')),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF10B981), foregroundColor: Colors.black),
                onPressed: _isLoading ? null : _registar,
                child: const Text('Submeter Registo'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ----------------- PAINEL DO PRODUTOR -----------------
class ProducerScreen extends StatefulWidget {
  final String uid;
  final String nome;
  const ProducerScreen({super.key, required this.uid, required this.nome});

  @override
  State<ProducerScreen> createState() => _ProducerScreenState();
}

class _ProducerScreenState extends State<ProducerScreen> {
  final _culturaController = TextEditingController();
  final _areaController = TextEditingController();
  final _qtdController = TextEditingController();
  final _obsController = TextEditingController();
  String _tipo = 'Plantio';

  Future<void> _registarManejo() async {
    if (_culturaController.text.isEmpty || _areaController.text.isEmpty || _qtdController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Preencha os campos obrigatórios.')));
      return;
    }

    try {
      final response = await http.post(
        Uri.parse('$apiUrl/manejo'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          "cultura": _culturaController.text,
          "area": _areaController.text,
          "tipo": _tipo,
          "quantidade": _qtdController.text,
          "observacao": _obsController.text,
          "uid_usuario": widget.uid
        }),
      );

      if (response.statusCode == 201) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Atividade de manejo gravada!')));
        _culturaController.clear();
        _areaController.clear();
        _qtdController.clear();
        _obsController.clear();
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro: $e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Painel do Produtor (${widget.nome})'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const LoginScreen())),
          )
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(controller: _culturaController, decoration: const InputDecoration(labelText: 'Cultura (ex: Milho)')),
            const SizedBox(height: 10),
            TextField(controller: _areaController, decoration: const InputDecoration(labelText: 'Área / Talhão (ex: Setor A)')),
            const SizedBox(height: 10),
            DropdownButtonFormField<String>(
              value: _tipo,
              items: ['Plantio', 'Colheita', 'Aplicação de Insumos', 'Manejo Geral']
                  .map((t) => DropdownMenuItem(value: t, child: Text(t)))
                  .toList(),
              onChanged: (val) => setState(() => _tipo = val!),
              decoration: const InputDecoration(labelText: 'Tipo de Operação'),
            ),
            const SizedBox(height: 10),
            TextField(controller: _qtdController, decoration: const InputDecoration(labelText: 'Quantidade (ex: 50 kg)')),
            const SizedBox(height: 10),
            TextField(controller: _obsController, decoration: const InputDecoration(labelText: 'Observações')),
            const SizedBox(height: 20),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF10B981), foregroundColor: Colors.black),
              onPressed: _registarManejo,
              child: const Text('Gravar Registo de Manejo'),
            ),
          ],
        ),
      ),
    );
  }
}

// ----------------- PAINEL DO ADMINISTRADOR -----------------
class AdminScreen extends StatefulWidget {
  final String uid;
  const AdminScreen({super.key, required this.uid});

  @override
  State<AdminScreen> createState() => _AdminScreenState();
}

class _AdminScreenState extends State<AdminScreen> {
  Map<String, dynamic> dadosAdmin = {};
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _carregarDashboard();
  }

  Future<void> _carregarDashboard() async {
    try {
      final response = await http.get(Uri.parse('$apiUrl/admin/dashboard/${widget.uid}'));
      if (response.statusCode == 200) {
        setState(() {
          dadosAdmin = jsonDecode(response.body);
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() => isLoading = false);
    }
  }

  Future<void> _alterarStatus(String uidAlvo, String novoStatus) async {
    try {
      await http.patch(
        Uri.parse('$apiUrl/admin/users/$uidAlvo/status'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"status": novoStatus}),
      );
      _carregarDashboard();
    } catch (e) {
      print(e);
    }
  }

  Future<void> _apagarUtilizador(String uidAlvo) async {
    try {
      await http.delete(Uri.parse('$apiUrl/admin/users/$uidAlvo'));
      _carregarDashboard();
    } catch (e) {
      print(e);
    }
  }

  @override
  Widget build(BuildContext context) {
    final metricas = dadosAdmin['metricas'] ?? {};
    final usuarios = dadosAdmin['usuarios_lista'] ?? {};

    return Scaffold(
      appBar: AppBar(
        title: const Text('Painel do Administrador'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const LoginScreen())),
          )
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Total de Utilizadores: ${metricas['total_usuarios'] ?? 0}'),
                  Text('Total de Registos de Manejo: ${metricas['total_registros'] ?? 0}'),
                  const Divider(height: 30),
                  const Text('Gestão de Utilizadores e Aprovações', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  const SizedBox(height: 10),
                  ...usuarios.entries.map<Widget>((entry) {
                    final u = entry.value;
                    final status = u['status'] ?? 'pending';
                    final role = u['role'] ?? 'user';

                    return Card(
                      color: const Color(0xFF1F2937),
                      margin: const EdgeInsets.symmetric(vertical: 6),
                      child: ListTile(
                        title: Text(u['nome'] ?? 'Sem nome', style: const TextStyle(fontWeight: FontWeight.bold)),
                        subtitle: Text('${u['email']}\nFunção: $role | Estado: $status'),
                        isThreeLine: true,
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            if (status == 'pending')
                              IconButton(
                                icon: const Icon(Icons.check_circle, color: Colors.green),
                                onPressed: () => _alterarStatus(entry.key, 'approved'),
                                tooltip: 'Aprovar Utilizador',
                              ),
                            IconButton(
                              icon: const Icon(Icons.delete, color: Colors.red),
                              onPressed: () => _apagarUtilizador(entry.key),
                              tooltip: 'Eliminar Utilizador',
                            ),
                          ],
                        ),
                      ),
                    );
                  }).toList(),
                ],
              ),
            ),
    );
  }
}
