import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const YouthUnemploymentApp());
}

class YouthUnemploymentApp extends StatelessWidget {
  const YouthUnemploymentApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Youth Job Creation Tool',
      theme: ThemeData(
        primarySwatch: Colors.indigo,
        useMaterial3: true,
      ),
      home: const PredictionScreen(),
    );
  }
}

class PredictionScreen extends StatefulWidget {
  const PredictionScreen({super.key});

  @override
  State<PredictionScreen> createState() => _PredictionScreenState();
}

class _PredictionScreenState extends State<PredictionScreen> {
  final _formKey = GlobalKey<FormState>();

  // Input Controllers
  final TextEditingController _countryController = TextEditingController(text: "Zambia");
  String _sex = "Female";

  // Historical years controllers (2014 - 2023)
  final Map<int, TextEditingController> _yearControllers = {
    2014: TextEditingController(text: "16.9"),
    2015: TextEditingController(text: "17.0"),
    2016: TextEditingController(text: "16.9"),
    2017: TextEditingController(text: "16.6"),
    2018: TextEditingController(text: "8.0"),
    2019: TextEditingController(text: "8.1"),
    2020: TextEditingController(text: "10.7"),
    2021: TextEditingController(text: "10.0"),
    2022: TextEditingController(text: "9.2"),
    2023: TextEditingController(text: "8.6"),
  };

  String _predictionResult = "";
  bool _isLoading = false;

  // Your live Render API endpoint URL
  final String _apiUrl = "https://linear-regression-task.onrender.com/predict";

  Future<void> _getPrediction() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _predictionResult = "";
    });

    // Construct the payload JSON matching your FastAPI Pydantic schema
    final Map<String, dynamic> requestBody = {
      "country_name": _countryController.text,
      "sex": _sex,
      "y2014": double.parse(_yearControllers[2014]!.text),
      "y2015": double.parse(_yearControllers[2015]!.text),
      "y2016": double.parse(_yearControllers[2016]!.text),
      "y2017": double.parse(_yearControllers[2017]!.text),
      "y2018": double.parse(_yearControllers[2018]!.text),
      "y2019": double.parse(_yearControllers[2019]!.text),
      "y2020": double.parse(_yearControllers[2020]!.text),
      "y2021": double.parse(_yearControllers[2021]!.text),
      "y2022": double.parse(_yearControllers[2022]!.text),
      "y2023": double.parse(_yearControllers[2023]!.text),
    };

    try {
      final response = await http.post(
        Uri.parse(_apiUrl),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode(requestBody),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> responseData = jsonDecode(response.body);
        final prediction = responseData["predicted_youth_unemployment_2024"];
        setState(() {
          _predictionResult = "Predicted 2024 Unemployment Rate: $prediction%";
        });
      } else {
        final errorDetail = jsonDecode(response.body)["detail"] ?? "Unprocessable inputs.";
        setState(() {
          _predictionResult = "Error: $errorDetail";
        });
      }
    } catch (e) {
      setState(() {
        _predictionResult = "Could not connect to the API server. Please check your internet connection.";
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Youth Job Creation Predictor', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.indigo,
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 1. Mission Header
              const Card(
                color: Color(0xFFE8EAF6),
                child: Padding(
                  padding: EdgeInsets.all(12.0),
                  child: Text(
                    "Our Mission: Identifying and predicting youth unemployment drivers globally to establish strategic youth job creation policies.",
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.indigo),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // 2. Demographic Entires (Country & Gender)
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _countryController,
                      decoration: const InputDecoration(
                        labelText: "Country",
                        border: OutlineInputBorder(),
                      ),
                      validator: (v) => v!.isEmpty ? "Required" : null,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      value: _sex,
                      decoration: const InputDecoration(
                        labelText: "Gender",
                        border: OutlineInputBorder(),
                      ),
                      items: ["Female", "Male"].map((g) {
                        return DropdownMenuItem(value: g, child: Text(g));
                      }).toList(),
                      onChanged: (val) => setState(() => _sex = val!),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),

              const Text(
                "Historical Youth Unemployment Rates (%)",
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 10),

              // 3. 10 Years Input Fields arranged in a grid for a neat, non-overlapping design
              GridView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  childAspectRatio: 2.8,
                  crossAxisSpacing: 12,
                  mainAxisSpacing: 12,
                ),
                itemCount: _yearControllers.length,
                itemBuilder: (context, index) {
                  int year = _yearControllers.keys.elementAt(index);
                  return TextFormField(
                    controller: _yearControllers[year],
                    keyboardType: const TextInputType.numberWithOptions(decimal: true),
                    decoration: InputDecoration(
                      labelText: "$year Rate (%)",
                      border: const OutlineInputBorder(),
                    ),
                    validator: (v) {
                      if (v == null || v.isEmpty) return "Required";
                      final parsed = double.tryParse(v);
                      if (parsed == null || parsed < 0.0 || parsed > 100.0) {
                        return "Enter 0-100";
                      }
                      return null;
                    },
                  );
                },
              ),
              const SizedBox(height: 28),

              // 4. "Predict" Button
              _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : ElevatedButton(
                      onPressed: _getPrediction,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.indigo,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                      child: const Text(
                        "Predict",
                        style: TextStyle(fontSize: 18, color: Colors.white, fontWeight: FontWeight.bold),
                      ),
                    ),
              const SizedBox(height: 24),

              // 5. Prediction Result Area
              if (_predictionResult.isNotEmpty)
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: _predictionResult.startsWith("Error") ? Colors.red.shade50 : Colors.green.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: _predictionResult.startsWith("Error") ? Colors.red : Colors.green,
                    ),
                  ),
                  child: Text(
                    _predictionResult,
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: _predictionResult.startsWith("Error") ? Colors.red : Colors.green.shade900,
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}