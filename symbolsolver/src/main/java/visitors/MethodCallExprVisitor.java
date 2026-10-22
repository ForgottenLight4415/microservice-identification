package visitors;

import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

import java.util.List;

public class MethodCallExprVisitor extends VoidVisitorAdapter<List> {

    @Override
    public void visit(MethodCallExpr visitor, List collector) {
        super.visit(visitor, collector);
        collector.add(visitor);
    }
}
