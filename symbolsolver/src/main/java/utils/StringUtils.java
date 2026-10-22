package utils;

import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.CoreDocument;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

public class StringUtils {


    private static StanfordCoreNLP pipeline;

    static {
        Properties props = new Properties();
        //props.setProperty("annotators", "tokenize, ssplit, pos, lemma, ner, parse, dcoref");
        props.setProperty("annotators", "tokenize, ssplit, pos, lemma");
        pipeline = new StanfordCoreNLP(props);
    }

    public static List<String> filterAndCleanText(String text, Set<String> stopWords) {
        return StringUtils.filterStopWords(StringUtils.lemmatize(String.join(" ", StringUtils.extractCamelCaseLower(text))), stopWords);
    }

    public static List<String> lemmatize(String text) {
        CoreDocument cd = new CoreDocument(String.join(" ", text));
        pipeline.annotate(cd);

        return cd.tokens().stream()
                .map(CoreLabel::lemma)
                .collect(Collectors.toList());
    }

    public static List<String> filterStopWords(List<String> words, Set<String> stopWords){
        return words.stream().filter(word -> !stopWords.contains(word)).collect(Collectors.toList());
    }

    public static Map<String, Integer> readClustersFromString(String string) {
        String pattern = "'([\\w\\.]*)'";
        String[] stringSplit = string.split("\\]");

        int group = 0;
        Map<String, Integer> clusters = new HashMap<>();
        Pattern p = Pattern.compile(pattern);

        for (String s : stringSplit) {
            Matcher m = p.matcher(s);
            while (m.find()) {
                clusters.put(m.group(1), group);
            }
            group++;
        }
        return clusters;
    }


    public static List<String> extractVariableType(String string) {

        List<String> strings = new ArrayList<>();
        String pattern = "(\\b\\w*\\b)(?!\\<)";
        Pattern p = Pattern.compile(pattern);
        Matcher m = p.matcher(string);

        while (m.find()) {
            if (!m.group(0).equals("")) {
                // TODO : REVIEW, previously used as toLowerCase() for metrics but it interfers currently
                // we need the camel case version to export the parsed information
                strings.add(m.group(0));
            }
        }

        // Set<String> stopTypes = new HashSet<>(Arrays.asList("integer", "int", "long", "string", "void", "object"));

        return strings; //.stream().filter(s -> !stopTypes.contains(s)).collect(Collectors.toList());

    }

    public static List<String> extractCamelCaseLower(String string) {
        List<String> extracted = new ArrayList<>();
        for (String s : string.split("(?<=[a-z])(?=[A-Z])")) {
            extracted.add(s.toLowerCase());
        }
        return extracted;
    }
}
