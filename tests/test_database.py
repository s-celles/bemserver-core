"""DB framework related tests"""
import sqlalchemy as sqla

import pytest

from bemserver_core.database import Base, db


class TestDatabase:
    @pytest.mark.usefixtures("database")
    def test_database_base_update(self):
        """Test update method of custom Base class"""

        class Test(Base):
            __tablename__ = "test_database_base_update"

            id = sqla.Column(sqla.Integer, primary_key=True)
            test_1 = sqla.Column(sqla.String(80), nullable=True)
            test_2 = sqla.Column(sqla.String(80), nullable=False)

        test = Test(test_1="test_1", test_2="test_2")
        assert test.test_1 == "test_1"
        assert test.test_2 == "test_2"

        test.update(test_1="test_11")
        assert test.test_1 == "test_11"
        test.update(test_1=None)
        assert test.test_1 is None

        # The nullable argument makes no difference here
        # This will only fail on commit
        test.update(test_2="test_21")
        assert test.test_2 == "test_21"
        test.update(test_2=None)
        assert test.test_2 is None

    @pytest.mark.usefixtures("database")
    def test_database_sort(self):
        """Test sort feature"""

        class Test(Base):
            __tablename__ = "test_database_sort"

            id = sqla.Column(sqla.Integer, primary_key=True)
            title = sqla.Column(sqla.String())
            severity = sqla.Column(
                sqla.Enum("Low", "High", "Critical", name="test_db_severity")
            )

        Test.__table__.create(bind=db.engine)

        mes_1 = Test(title="3 Hello", severity="Low")
        mes_2 = Test(title="2 Hello", severity="Critical")
        mes_3 = Test(title="1 Hello", severity="High")
        db.session.add(mes_1)
        db.session.add(mes_2)
        db.session.add(mes_3)
        db.session.commit()

        ret = Test.get(sort=["severity"]).all()
        assert ret == [mes_1, mes_3, mes_2]
        ret = Test.get(sort=["+severity"]).all()
        assert ret == [mes_1, mes_3, mes_2]
        ret = Test.get(sort=["-severity"]).all()
        assert ret == [mes_2, mes_3, mes_1]

        ret = Test.get(sort=["title"]).all()
        assert ret == [mes_3, mes_2, mes_1]

        mes_4 = Test(title="2 Hello", severity="Low")
        mes_5 = Test(title="1 Hello", severity="Critical")
        mes_6 = Test(title="3 Hello", severity="High")
        db.session.add(mes_4)
        db.session.add(mes_5)
        db.session.add(mes_6)
        db.session.commit()

        ret = Test.get(sort=["-severity", "title"]).all()
        assert ret == [mes_5, mes_2, mes_3, mes_6, mes_4, mes_1]
